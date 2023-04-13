import os.path
import os
from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from django.views.decorators.csrf import csrf_exempt
import jwt
import datetime
from .constants import Addemployee
from AttendanceApp.models import Admin
from AttendanceApp.serializers import EmployeeSerializer, AdminSerializer
# from Attendance_Management.settings import SIMPLE_JWT,REST_FRAMEWORK
from PIL import Image
import io
# django file storage
from gridfs import GridFS
from pymongo import MongoClient

class EmployeeView(APIView):
    @csrf_exempt
    def post(self, request):
        proof_file = request.FILES['proof']
        file_contents1 = proof_file.read()
        certificates_file = request.FILES['certificates']
        file_contents = certificates_file.read()
        # imgsrc_profile = request.FILES['imgSrc']
        # file_contents3 = imgsrc_profile.read()
        serializer = EmployeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = serializer.save()
        # Store the files in GridFS
        client = MongoClient("mongodb://localhost:27017/")
        db = client["data"]
        fs = GridFS(db)
        # certificates_filename =employee.name+".pdf"
        proof_file_id = fs.put(file_contents1, filename=employee.id+".pdf", employee_id=employee.id)
        certificates_file_id = fs.put(file_contents, filename=employee.name+".pdf", employee_id=employee.id)
        # imgsrc_profile_id = fs.put(file_contents3, filename = employee.name + "-" + str(employee.id) + ".pdf", employee_id=employee.id)
        return Response({'message': 'New Employee Has Been Added Successfully'})




class AdminLogin(APIView):
    @csrf_exempt
    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        user = Admin.objects.filter(email=email).first()
        if user is None:
            raise AuthenticationFailed('User not found!')
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }
        # token = jwt.encode(payload, 'secret', algorithm='HS256').decode('utf-8')
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token,
            'email': user.email,
                    'name': user.name,
                    'role': user.role,
                    'mobile': user.mobile
        }
        return response


class AdminReg(APIView):
    @csrf_exempt
    def post(self, request):
        serializer = AdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
