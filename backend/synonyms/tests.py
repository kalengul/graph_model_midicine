from django.urls import reverse
from rest_framework.test import APITestCase
from synonyms.models import SynonymGroup, Synonym
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model


class SynonymAPITestCase(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)

        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token.key}"}
        self.group = SynonymGroup.objects.create(name="Кластер 1")

        self.synonym1 = Synonym.objects.create(name="слово 1", group=self.group, is_changed=False)
        self.synonym2 = Synonym.objects.create(name="слово 2", group=self.group, is_changed=True)

    def test_get_synonym_groups(self):
        url = reverse("get_synonym_groups")
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["result"]["status"], 200)
        self.assertTrue(any(g["sg_name"] == "Кластер 1" for g in response.data["data"]))

    def test_post_synonym_group(self):
        url = reverse("get_synonym_groups")
        payload = {"name": "Новая группа"}
        response = self.client.post(url, data=payload, format="json", **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["result"]["status"], 200)
        self.assertEqual(response.data["data"]["name"], "Новая группа")
        self.assertEqual(response.data["data"]["is_completed"], False)

    def test_get_synonym_list(self):
        url = reverse("get_synonym_list")
        response = self.client.get(url, data={"sg_id": self.group.id}, **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["result"]["status"], 200)
        self.assertEqual(len(response.data["data"]), 2)
        self.assertIn("s_id", response.data["data"][0])

    def test_get_synonym_list_without_sg_id(self):
        url = reverse("get_synonym_list")
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["result"]["message"], "Не указан параметр sg_id")

    def test_create_synonyms(self):
        url = reverse("create_synonym")
        payload = {
            "sg_id": self.group.id,
            "names": ["слово A", "слово B"]
        }
        response = self.client.post(url, data=payload, format="json", **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["result"]["status"], 200)
        self.assertEqual(len(response.data["data"]), 2)
        self.assertEqual(response.data["data"][0]["is_changed"], False)

    def test_update_synonyms(self):
        url = reverse("update_synonym_list")
        payload = {
            "sg_id": self.group.id,
            "list_id": [
                {"s_id": self.synonym1.id, "status": True},
                {"s_id": self.synonym2.id, "status": False}
            ]
        }
        response = self.client.put(url, data=payload, format="json", **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["result"]["status"], 200)
        self.assertIn(self.synonym1.id, response.data["data"]["updated_ids"])
        self.assertIn(self.synonym2.id, response.data["data"]["updated_ids"])

    def test_update_synonyms_invalid(self):
        url = reverse("update_synonym_list")
        response = self.client.put(url, data={}, format="json", **self.auth_headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["result"]["message"], "Неверные данные")

    def test_unauthorized_access(self):
        url = reverse("get_synonym_groups")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
