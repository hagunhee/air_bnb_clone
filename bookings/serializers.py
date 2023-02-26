from django.utils import timezone
from rest_framework import serializers
from .models import Booking


class CreateRoomBookingSerializer(serializers.ModelSerializer):

    # check_in,check_out이 필수값이 되도록 첵크인, 아웃은 이 규격으로 들어오라고 디폴트로 설정해줌.
    check_in = serializers.DateField()
    check_out = serializers.DateField()

    class Meta:
        model = Booking
        fields = (
            "check_in",
            "check_out",
            "guests",
        )

        # is_valid 메서드를 통해 과거의 날짜는 false가 나오도록 커스터마이징함.
        # 아래에서 validate_하고 validate하고 싶은 field를 넣으면 됨
        # validate(self, alldata) 셀프와 모든 데이터를 받는다.

    def validate_check_in(self, value):
        now = timezone.localtime(timezone.now()).date()
        if now > value:
            raise serializers.ValidationError("Can't book in the past!")
        return value

    def validate_check_out(self, value):
        now = timezone.localtime(timezone.now()).date()
        if now > value:
            raise serializers.ValidationError("Can't book in the past!")
        return value

    def validate(self, data):
        if data["check_out"] <= data["check_in"]:
            raise serializers.ValidationError("Check in should be amaller than check out.")
        if Booking.objects.filter(
            # want 5.10~ 20
            check_in__lte=data["check_out"],  # 내가 나가기 전에 기존에 들어와있는게 있으며,
            check_out__gte=data["check_in"],  # 덧붙여서 내가 들어오고나서 기존에 나가는 예약이 있는지.
        ).exists():
            raise serializers.ValidationError("Those(or some) of those dates are already taken.")
        return data


class PublicBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = (
            "pk",
            "check",
            "check_in",
            "check_out",
            "experience_time",
            "guests",
        )
