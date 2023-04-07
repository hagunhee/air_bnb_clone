from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import (
    NotFound,
    ParseError,
    PermissionDenied,
)
from .serializers import AmenitySerializer, RoomListSerializer, RoomDetailSerializer
from reviews.serializers import ReviewSerializer
from medias.serializers import PhotoSerializer
from categories.models import Category
from .models import Amenity, Room
from bookings.models import Booking
from bookings.serializers import PublicBookingSerializer, CreateRoomBookingSerializer


class Amenities(APIView):
    def get(self, request):
        all_amenities = Amenity.objects.all()
        serializer = AmenitySerializer(all_amenities, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AmenitySerializer(data=request.data)
        if serializer.is_valid():
            amenity = serializer.save()
            return Response(
                AmenitySerializer(amenity).data,
            )
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class AmenityDetail(APIView):
    def get_object(self, pk):
        try:
            return Amenity.objects.get(pk=pk)
        except Amenity.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        amenity = self.get_object(pk)
        serializer = AmenitySerializer(amenity)
        return Response(serializer.data)

    def put(self, request, pk):
        amenity = self.get_object(pk)
        serializer = AmenitySerializer(
            amenity,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            updatead_amenity = serializer.save()
            return Response(AmenitySerializer(updatead_amenity).data)
        else:
            return Response(
                serializer.errors,
                status=HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, pk):
        amenity = self.get_object(pk)
        amenity.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class Rooms(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        all_rooms = Room.objects.all()
        serializer = RoomListSerializer(
            all_rooms,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    def post(self, request):

        serializer = RoomDetailSerializer(data=request.data)

        if serializer.is_valid():
            category_pk = request.data.get("category")
            amenity_pks = request.data.get("amenities")
            if not category_pk:
                raise ParseError("Category is required.")
            try:
                category = Category.objects.get(pk=category_pk)
                if category.kind == Category.CategoryKindChoices.EXPERIENCES:
                    raise ParseError("The category kind should be 'rooms'")
            except Category.DoesNotExist:
                raise ParseError("Category not found")

            try:
                with transaction.atomic():
                    new_room = serializer.save(
                        owner=request.user,
                        category=category,
                    )
                    if amenity_pks:
                        for amenity_pk in amenity_pks:
                            amenity = Amenity.objects.get(pk=amenity_pk)
                            new_room.amenities.add(amenity)
            except Amenity.DoesNotExist:
                raise ParseError("Amenity not found!")
            except Exception as e:
                raise ParseError(e)
            serializer = RoomDetailSerializer(new_room, context={"request": request})
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class RoomDetail(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        room = self.get_object(pk)
        # context는 내가 원하는 context를 전달 할 수 있게 해줌.
        # 그로인해 많은 것을 할 수 있다. serialize.py의 is_owner메서드같은....
        # 그러면 오너인 방들에만 수정권한을 준다던지 할 수 있음. 인스타그램의 라이크여부에 따라 하트모양
        serializer = RoomDetailSerializer(
            room,
            context={"request": request},
        )
        return Response(serializer.data)

    def delete(self, request, pk):

        room = self.get_object(pk)
        if room.owner != request.user:
            raise PermissionDenied
        room.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    def put(self, request, pk):
        room = self.get_object(pk)
        if room.owner != request.user:
            raise PermissionDenied
        serializer = RoomDetailSerializer(
            room,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            category_pk = request.data.get("category")
            if category_pk:
                try:
                    category = Category.objects.get(pk=category_pk)
                    if category.kind != Room:
                        raise ParseError("The category kind should be 'rooms'")
                except Category.DoesNotExist:
                    ParseError(detail="Category not found")

            try:
                with transaction.atomic():
                    if category_pk:
                        updated_room = serializer.save(category=category)
                    else:
                        updated_room = serializer.save()
                    amenities = request.data.get("amenities")

                    if amenities:
                        room.amenities.clear()
                        for amenity_pk in amenities:
                            amenity = Amenity.objects.get(pk=amenity_pk)
                            updated_room.amenities.add(amenity)
                    serializer = RoomDetailSerializer(
                        updated_room,
                        context={"request": request},
                    )

                return Response(serializer.data)
            except Exception as e:
                raise ParseError(e)
        else:
            return Response(serializer.errors)


class RoomReviews(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        # print(request.query_params) URL에서 보낸 파라미터 ?page=4를 읽어준다.
        try:
            # get 메소드이기 때문에 디폴트를 정할 수 있다. 현재는 default = 1인 코드.
            page = request.query_params.get("page", 1)
            # 현재 파라미터는 str로 들어오고 있다.
            page = int(page)
        except ValueError:
            # page=dasf 같은 파라미터값을 받더라도 1페이지를 출력해줌
            page = 1
        page_size = 3
        start = (page - 1) * page_size
        end = start + page_size
        room = self.get_object(pk)
        serializer = ReviewSerializer(
            # 대괄호로 인덱스 범위를 설정해줄 수 있다. pagination
            # 0:4는 리스트안에 a,b,c,d,e가 있을 때 offset인 0 인덱스는 포함하지만('a')
            # Limit 4 인덱스는 포함하지않고 이전에서 끝난다.
            room.reviews.all()[start:end],
            many=True,
        )
        return Response(serializer.data)

    def post(self, request, pk):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(user=request.user, room=self.get_object(pk))
            serializer = ReviewSerializer(review)
            return Response(serializer.data)


class RoomAmenities(APIView):
    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):

        try:
            page = request.query_params.get("page", 1)
            page = int(page)
        except ValueError:
            page = 1

        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        room = self.get_object(pk)
        serializer = AmenitySerializer(room.amenities.all()[start:end], many=True)
        return Response(serializer.data)


class RoomPhotos(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        room = self.get_object(pk)
        if request.user != room.owner:
            raise PermissionDenied
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            # 룸을 만들 때 카테고리를 설정하듯, 룸을 같이 보내줘야함.
            photo = serializer.save(room=room)
            serializer = PhotoSerializer(photo)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class RoomBookings(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except:
            raise NotFound

    def get(self, request, pk):
        room = self.get_object(pk)
        # timezond.now() = 기준인 UTC 시간대를 찍어줌. timezone.localtime(timezone.now()) = UTC를 현지시간으로 변경
        # 룸부킹 모델에 맞춰 뒤에 date를 적어주어 datetime이 아닌 date만 반환함.
        # 체크인 데이터가 현재 날짜보다 큰 데이터를 찾아줌.
        now = timezone.localtime(timezone.now()).date()
        bookings = Booking.objects.filter(
            room=room,
            kind=Booking.BookingKindChoices.ROOM,
            check_in__gt=now,
        )
        # Bookings = Booking.objects.filter(room__pk=pk)으로 작성하면 룸을 먼저 찾아낼 필요가 없다.
        # 다만, 이런식으로 하면 룸이 존재하지않거나, 예약이 존재하지 않으면 똑같이 빈 리스트를 반환한다.
        serializer = PublicBookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        room = self.get_object(pk)
        # 모델을 살펴보면 guests만 required이기때문에 새로 만들어줌..
        serializer = CreateRoomBookingSerializer(data=request.data)
        # is_valid 메서드를 통해 과거의 날짜는 false가 나오도록 커스터마이징함.
        if serializer.is_valid():
            booking = serializer.save(
                room=room,
                user=request.user,
                kind=Booking.BookingKindChoices.ROOM,
            )
            serializer = PublicBookingSerializer(booking)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
