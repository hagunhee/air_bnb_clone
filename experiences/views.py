from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.response import Response
from .models import Perk, Experience
from . import serializers
from categories.models import Category
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from reviews.serializers import ReviewSerializer
from reviews.models import Review
from medias.serializers import PhotoSerializer
from bookings.models import Booking
from bookings.serializers import (
    PublicBookingSerializer,
    CreateRoomBookingSerializer,
    CreateExperienceBookingSerializer,
)


class Experiences(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        all_experiences = Experience.objects.all()
        serializer = serializers.ExperienceListSerializer(
            all_experiences,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    def post(self, request):

        serializer = serializers.ExperienceDetailSerializer(data=request.data)

        if serializer.is_valid():
            category_pk = request.data.get("category")
            perk_pks = request.data.get("perks")
            if not category_pk:
                raise ParseError("Category is required.")
            try:
                category = Category.objects.get(pk=category_pk)
                if category.kind == Category.CategoryKindChoices.ROOMS:
                    raise ParseError("The category kind should be 'experiences'")
            except Category.DoesNotExist:
                raise ParseError("Category not found")

            try:
                with transaction.atomic():
                    new_experience = serializer.save(
                        host=request.user,
                        category=category,
                    )
                    if perk_pks:
                        for perk_pk in perk_pks:
                            perk = Perk.objects.get(pk=perk_pk)
                            print(perk.name)
                            new_experience.perks.add(perk)
            except Perk.DoesNotExist:
                raise ParseError("Perk not found")
            except Exception as e:
                raise ParseError(e)
            serializer = serializers.ExperienceDetailSerializer(
                new_experience, context={"request": request}
            )
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class ExperienceDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        experience = self.get_object(pk)
        serializer = serializers.ExperienceDetailSerializer(
            experience,
            context={"request": request},
        )
        return Response(serializer.data)

    def delete(self, request, pk):
        experience = self.get_object(pk)
        if experience.host != request.user:
            raise PermissionError
        experience.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    def put(self, request, pk):

        experience = self.get_object(pk)
        if experience.host != request.user:
            raise PermissionError
        serializer = serializers.ExperienceDetailSerializer(
            experience, data=request.data, partial=True
        )

        if serializer.is_valid():
            category_pk = request.data.get("category")
            if category_pk:
                try:
                    category = Category.objects.get(pk=category_pk)
                    if category.kind != Experience:
                        raise ParseError("The category kind should be 'experience'")
                except Category.DoesNotExist:
                    ParseError("Category not found")
            try:
                with transaction.atomic():
                    if category_pk:
                        updated_experience = serializer.save(category=category)
                    else:
                        updated_experience = serializer.save()
                        perks = request.data.get("perks")

                    if perks:
                        experience.perks.clear()
                        for perk_pk in perks:
                            perk = Perk.objects.get(pk=perk_pk)
                            updated_experience.perks.add(perk)
                serializer = serializers.ExperienceDetailSerializer(
                    updated_experience, context={"request": request}
                )
                return Response(serializer.data)
            except Exception as e:
                raise ParseError(e)
        else:
            return Response(serializer.errors)


class Perks(APIView):
    def get(self, request):
        all_perks = Perk.objects.all()
        serializer = serializers.PerkSerializer(all_perks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = serializers.PerkSerializer(data=request.data)
        if serializer.is_valid():
            perk = serializer.save()
            return Response(serializers.PerkSerializer(perk).data)
        else:
            return Response(serializer.errors)


class PerkDetail(APIView):
    def get_object(self, pk):
        try:
            return Perk.objects.get(pk=pk)
        except Perk.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        perk = self.get_object(pk)
        serializer = serializers.PerkSerializer(perk)
        return Response(serializer.data)

    def put(self, request, pk):
        perk = self.get_object(pk)
        serialzer = serializers.PerkSerializer(perk, data=request.data, partial=True)
        if serialzer.is_valid():
            updated_perk = serialzer.save()
            return Response(
                serializers.PerkSerializer(updated_perk).data,
            )
        else:
            return Response(serialzer.errors)

    def delete(self, request, pk):
        perk = self.get_object(pk)
        perk.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class ExperienceReviews(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        try:
            page = request.query_params.get("page", 1)
            page = int(page)
        except ValueError:
            page = 1
        page_size = 3
        start = (page - 1) * page_size
        end = start + page_size
        experience = self.get_object(pk)
        serializer = ReviewSerializer(
            experience.reviews.all()[start:end],
            many=True,
        )
        return Response(serializer.data)

    def post(self, request, pk):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(user=request.user, experience=self.get_object(pk))
            serializer = ReviewSerializer(review)
            return Response(serializer.data)


class ExperienceReviewsDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk, review_pk):
        try:
            experience = Experience.objects.get(pk=pk)
            review = Review.objects.get(pk=review_pk, experience=experience)
            return review
        except review.DoesNotExist:
            raise NotFound()

    def get(self, request, pk, review_pk):
        review = self.get_object(pk, review_pk)
        serializer = ReviewSerializer(review)
        return Response(serializer.data)

    def delete(self, request, pk, review_pk):
        review = self.get_object(pk, review_pk)
        if review.user != request.user:
            raise PermissionError
        review.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class ExperiencePhotos(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        experience = self.get_object(pk)
        if experience.host != request.user:
            raise PermissionError
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            photo = serializer.save(experience=experience)
            serializer = PhotoSerializer(photo)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class ExperienceBookings(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        experience = self.get_object(pk)
        now = timezone.localtime(timezone.now())
        bookings = Booking.objects.filter(
            experience=experience,
            kind=Booking.BookingKindChoices.EXPERIENCE,
            check_in__gt=now,
        )
        serializer = PublicBookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        experience = self.get_object(pk)
        serializer = CreateExperienceBookingSerializer(data=request.data)
        if serializer.is_valid():
            booking = serializer.save(
                experience=experience,
                user=request.user,
                kind=Booking.BookingKindChoices.EXPERIENCE,
            )
            serializer = PublicBookingSerializer(booking)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
