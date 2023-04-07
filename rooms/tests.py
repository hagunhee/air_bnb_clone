from rest_framework.test import APITestCase
from . import models
from users.models import User

# 테스트 코드는 전부 똑같다. 상태코드를 확인하고,
# 예상했떤 것과 같은 name이 나오는지 확인한다.
# 장고가 테스트해주길 원한다면 'test_'로 시작하는 메서드로 실행을 해야한다.
class TestAmenities(APITestCase):
    URL = "/api/v1/rooms/amenities/"
    NAME = "Amenity Test"
    DESC = "Amenity Des"

    # setUp메서드는 다른 모든 테스트들이 실행되기 전에 수행된다.
    def setUp(self):
        models.Amenity.objects.create(
            name=self.NAME,
            description=self.DESC,
        )

    # test는 코드가 작동해서 실행되지만 데이터베이스를 테스트용으로 새것으로 새로 만들기때문에
    # json을 열어보면 리스트안에 내용이 없다.
    def test_all_amenities(self):
        response = self.client.get(self.URL)
        data = response.json()
        self.assertIsInstance(
            data,
            list,
        )
        self.assertEqual(
            len(data),
            1,
        )
        self.assertEqual(
            data[0]["name"],
            self.NAME,
        )
        self.assertEqual(
            data[0]["description"],
            self.DESC,
        )

    def test_create_amenity(self):

        new_amenity_name = "New Amenity"
        new_amenity_description = "New Amenity Desc"
        # URL로 데이터를 post한다
        response = self.client.post(
            self.URL,
            data={"name": new_amenity_name, "description": new_amenity_description},
        )
        data = response.json()
        self.assertEqual(
            response.status_code,
            200,
            "Not 200 status code",
        )
        self.assertEqual(
            data["name"],
            new_amenity_name,
        )
        self.assertEqual(
            data["description"],
            new_amenity_description,
        )

        response = self.client.post(self.URL)
        data = response.json()

        self.assertEqual(response.status_code, 400)
        # name이라는 member가 data라는 컨테이너 안에 있는지 확인해보는 것.
        self.assertIn("name", data)


class TestAmenity(APITestCase):

    NAME = "Amenity Test"
    DESC = "Amenity Des"

    def setUp(self):
        models.Amenity.objects.create(
            name=self.NAME,
            description=self.DESC,
        )

    def test_amenity_not_found(self):

        response = self.client.get("/api/v1/rooms/amenities/2")

        self.assertEqual(response.status_code, 404)

    def test_get_amenity(self):

        response = self.client.get("/api/v1/rooms/amenities/1")
        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(
            data["name"],
            self.NAME,
        )
        self.assertEqual(data["description"], self.DESC)

    def test_put_amenity(self):

        failed_name = "hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhi"

        response = self.client.put(
            "/api/v1/rooms/amenities/1",
            data={"name": self.NAME, "description": self.DESC},
        )

        data = response.json()
        self.assertEqual(data["name"], self.NAME)
        self.assertEqual(data["description"], self.DESC)
        self.assertEqual(response.status_code, 200)

        fail_response = self.client.put(
            "/api/v1/rooms/amenities/1",
            data={"name": failed_name},
        )
        data = fail_response.json()
        self.assertEqual(fail_response.status_code, 400)

    def test_delete_amenity(self):

        response = self.client.delete("/api/v1/rooms/amenities/1")

        self.assertEqual(response.status_code, 204)


class TestRoom(APITestCase):
    def setUp(self):
        user = User.objects.create(
            username="test",
        )
        user.set_password("123")
        user.save()
        self.user = user

    def test_create_room(self):

        response = self.client.post("/api/v1/rooms/")
        self.assertEqual(response.status_code, 403)

        """        self.client.login(
                username="test",
            password="123",
        )
        """
        # forcelogin을 사용하면 비밀번호가 필요없다.
        self.client.force_login(self.user)
        response = self.client.post("/api/v1/rooms/")
        print(response.json())
