import random
import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient
from rest_framework.status import is_success

@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make('Course', *args, **kwargs)

    return factory


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make('Student', *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_get_first_course(client, course_factory, student_factory):
    students = student_factory(_quantity=5)
    course = course_factory(students=students)

    response = client.get(reverse('courses-detail', args=[course.id]))

    assert is_success(response.status_code)
    assert response.json()['id'] == course.id
    assert response.json()['name'] == course.name


@pytest.mark.django_db
def test_get_list_courses(client, student_factory, course_factory):
    students = student_factory(_quantity=5)
    courses = course_factory(students=students, _quantity=5)

    response = client.get('/courses/')

    assert is_success(response.status_code)
    assert len(response.json()) == len(courses)


@pytest.mark.django_db
def test_filter_course_id(client, student_factory, course_factory):
    students = student_factory(_quantity=5)
    courses = course_factory(students=students, _quantity=5)
    id_course = random.choice(courses).id

    response = client.get('/courses/', {'id': id_course})

    assert is_success(response.status_code)
    assert response.json()[0]
    assert response.json()[0]['id'] == id_course


@pytest.mark.django_db
def test_filter_course_name(client, student_factory, course_factory):
    students = student_factory(_quantity=5)
    courses = course_factory(students=students, _quantity=5)
    course = random.choice(courses)

    response = client.get('/courses/', {'name': course.name})

    assert is_success(response.status_code)
    assert response.json()[0]['id'] == course.id
    assert response.json()[0]['name'] == course.name


@pytest.mark.django_db
def test_create_course(client):
    course = {'name': 'test_creation'}

    response = client.post('/courses/', course)
    get_response = client.get('/courses/', {'name': course['name']})

    assert is_success(response.status_code)
    assert get_response.json()[0]
    assert get_response.json()[0]['name'] == course['name']


@pytest.mark.django_db
def test_course_update(client, course_factory, student_factory):
    students = student_factory(_quantity=3)
    course_old = course_factory(students=students)
    course_new = course_factory(students=students)

    response = client.patch(reverse('courses-detail', args=[course_old.id]), {'name': course_new.name})
    get_response = client.get(reverse('courses-detail', args=[course_old.id]), {'id': course_old.id})

    assert is_success(response.status_code)
    assert response.json()['id'] == course_old.id and response.json()['name'] == course_new.name
    assert get_response.json()['id'] == course_old.id and get_response.json()['name'] == course_new.name


@pytest.mark.django_db
def test_delete_course(client, course_factory, student_factory):
    students = student_factory(_quantity=5)
    courses = course_factory(students=students, _quantity=5)
    random_course = random.choice(courses)

    response = client.delete(reverse('courses-detail', args=[random_course.id]))
    response_get = client.get(reverse('courses-list'))

    ids = [course['id'] for course in response_get.json()]

    assert is_success(response.status_code)
    assert random_course.id not in ids
