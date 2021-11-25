from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import *

from .services.returnStatsForm import *
from .services.sendSMTP import send as sendEmail

from datetime import datetime, timedelta, date
import random, re


@method_decorator(csrf_exempt, name='dispatch')
class requestEmailAuth(APIView):
    def post(self, request):
        try:
            email = request.data['email']
        except (KeyError, ValueError):
            return JsonResponse(BAD_REQUEST_400(message='Some Values are missing', data={}), status=400)
        try:
            User.objects.get(email=email)
            return JsonResponse(OK_200(data={"isEmailExist": True, "emailSent": False}), status=200)
        except ObjectDoesNotExist:
            pass
        try:
            email_name, domain_part = email.strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            email = email_name + '@' + domain_part.lower()
        emailCheck = re.compile('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        if not emailCheck.match(email) is not None:
            return JsonResponse(CUSTOM_CODE(data={"isEmailExist": False, "emailSent": False}, message='Invalid E-mail Form', status=400), status=200)
        code = ''
        for x in range(6):
            num = random.randrange(0, 10)
            code += str(num)
        sendEmail(code, email)
        authModel = emailAuth(
            mail=email,
            authCode=code,
            isAuthed=False
        )
        authModel.save()
        return JsonResponse(OK_200(data={"isEmailExist": False, "emailSent": True}), status=200)

    def put(self, request):
        try:
            email = request.query_params['email']
            auth = request.data['auth']
        except (KeyError, ValueError):
            return JsonResponse(BAD_REQUEST_400(message='Some Values are missing', data={}), status=400)
        try:
            authModel = emailAuth.objects.get(mail=email)
        except ObjectDoesNotExist:
            return JsonResponse(CUSTOM_CODE(status=400, data={}, message='There is no E-mail'), status=400)
        if not authModel.authCode == auth:
            return JsonResponse(CUSTOM_CODE(status=401, data={}, message='invalid auth code'), status=401)
        validTimeChecker = timezone.now() - timedelta(minutes=30)
        if authModel.requestTime < validTimeChecker:
            return JsonResponse(CUSTOM_CODE(status=410, message='time limit exceeded', data={}), status=410)
        authModel.isAuthed = True
        authModel.save()
        return JsonResponse(OK_200(data={}), status=200)


@method_decorator(csrf_exempt, name='dispatch')
class signupInfoInput(APIView):
    def post(self, request):
        returnData = {
            "emailExists": False,
            "validNickname": False,
            "validPassword": False
        }
        try:
            email = request.data['email']
            nickname = request.data['nickname']
            passwd = str(request.data['passwd'])
            region = request.data['region']
            role = request.data['role']
        except (KeyError, ValueError):
            return JsonResponse(BAD_REQUEST_400(message='Some Values are missing', data=returnData), status=400)
        try:
            authModel = emailAuth.objects.get(mail=email)
            if authModel.isAuthed:
                pass
            else:
                raise ObjectDoesNotExist
        except ObjectDoesNotExist:
            return JsonResponse(CUSTOM_CODE(status=403, message='There is no E-mail', data=returnData), status=403)
        try:
            User.objects.get(username=nickname)
        except ObjectDoesNotExist:
            returnData['validNickname'] = True
        try:
            int(passwd)
            if not passwd.__len__() == 6:
                raise TypeError
            else:
                returnData['validPassword'] = True
        except (TypeError, ValueError):
            pass
        if returnData['validPassword']:
            try:
                userModel = User.objects.create_user(
                    email=email,
                    username=nickname,
                    password=passwd,
                    region=region
                )
                userModel.save()
                userInfoModel = userInfo(
                    user=userModel,
                    role=role
                )
                userInfoModel.save()
                authModel.delete()
                return JsonResponse(OK_200(data=returnData), status=200)
            except (KeyError, ValueError):
                return JsonResponse(BAD_REQUEST_400(message='Some Values are missing', data=returnData), status=400)
            except IntegrityError:
                returnData["validNickname"] = False
        return JsonResponse(CUSTOM_CODE(status=406, data=returnData, message='invalid value'))


@method_decorator(csrf_exempt, name='dispatch')
class signinAPI(APIView):
    def post(self, request):
        try:
            nickname = request.data['nickname']
            passwd = request.data['passwd']
        except (KeyError, ValueError):
            return JsonResponse(BAD_REQUEST_400(message='Some Values are missing', data={}), status=400)
        user = authenticate(username=nickname, password=passwd)
        if user is not None:
            try:
                token = Token.objects.create(user=user)
            except IntegrityError:
                token = Token.objects.get(user=user)
            return JsonResponse(OK_200(data={"token": token.key}), status=200)
        return JsonResponse(CUSTOM_CODE(status=401, message="Invalid info", data={"token": ""}), status=401)


@method_decorator(csrf_exempt, name='dispatch')
class userAPI(APIView):
    def delete(self, request):
        if not request.user.is_authenticated or request.user.is_anonymous:
            return JsonResponse(BAD_REQUEST_400(message='Some Values are missing', data={}), status=400)
        request.user.delete()
        return JsonResponse(OK_200(data={}), status=200)


@method_decorator(csrf_exempt, name='dispatch')
class garbage_output_api(APIView):
    def post(self, request):
        returnData = {"amount": 0}
        if not request.user.is_authenticated or request.user.is_anonymous:
            return JsonResponse(BAD_REQUEST_400(message='Some Values are missing', data=returnData), status=400)
        try:
            year = request.data['year']
            month = request.data['month']
            amount = request.data['amount']
        except (KeyError, ValueError):
            return JsonResponse(BAD_REQUEST_400(message='Some Values are missing', data=returnData), status=400)
        if int(month) > 12:
            return JsonResponse(BAD_REQUEST_400(message='Invalid month', data=returnData), status=400)
        try:
            garbageModel = garbage_output.objects.get(user=request.user, date_year=int(year), date_month=int(month))
        except ObjectDoesNotExist:
            garbageModel = garbage_output(
                user=request.user,
                date_year=int(year),
                date_month=int(month)
            )
            garbageModel.save()
        try:
            garbageModel.amount += int(amount)
            garbageModel.save()
        except ValueError:
            return JsonResponse(BAD_REQUEST_400(message='Invalid amount', data=returnData, status=400))
        returnData["amount"] = int(garbageModel.amount)
        return JsonResponse(OK_200(data=returnData, status=200), status=200)

    def get(self, request):
        returnData = {"amount": 0}
        if not request.user.is_authenticated or request.user.is_anonymous:
            return JsonResponse(BAD_REQUEST_400(message='Some Values are missing', data=returnData), status=400)
        try:
            year = request.query_params['year']
            month = request.query_params['month']
        except (KeyError, ValueError):
            return JsonResponse(BAD_REQUEST_400(message='Some Values are missing', data=returnData), status=400)
        if int(month) > 12:
            return JsonResponse(BAD_REQUEST_400(message='Invalid month', data=returnData), status=400)
        try:
            garbageModel = garbage_output.objects.get(user=request.user, date_year=int(year), date_month=int(month))
        except ObjectDoesNotExist:
            return JsonResponse(OK_200(data=returnData), status=200)
        returnData["amount"] = int(garbageModel.amount)
        return JsonResponse(OK_200(data=returnData), status=200)


@method_decorator(csrf_exempt, name='dispatch')
class marketPostAPI(APIView):
    def post(self, request):
        returnData = {"pk": 0}
        if not request.user.is_authenticated or request.user.is_anonymous:
            return JsonResponse(BAD_REQUEST_400(message='Some Values are missing', data=returnData), status=400)
        try:
            postKind = request.data['postKind']
            trashKind = request.data['trashKind']
            content = request.data['content']
            qty = request.data['qty']
        except (KeyError, ValueError):
            return JsonResponse(BAD_REQUEST_400(message='Some Values are missing', data=returnData), status=400)
        marketPostModel = marketPost(
            postKind=postKind,
            trashKind=trashKind,
            qty=qty,
            content=content,
            location=request.user.region,
            author=request.user
        )
        marketPostModel.save()
        returnData["pk"] = marketPostModel.primaryKey
        try:
            imageList = request.FILES.getlist['image']
            imageCount = 1
            for image in imageList:
                imageModel = marketPostImage(postModel=marketPostModel, image=image, order=imageCount)
                imageModel.save()
                imageCount += 1
        except (KeyError, ValueError):
            pass
        return JsonResponse(OK_200(data=returnData))

    def get(self, request):
        returnData = {
            "postList": []
        }
        try:
            pk = request.query_params['pk']
        except (KeyError, ValueError):
            try:
                post_list = marketPost.objects.all().order_by('created_at')
                post_list = list(post_list)
            except ObjectDoesNotExist:
                return JsonResponse(OK_200(data=returnData), status=200)
            for post in post_list:
                postForm = {
                    'pk': post.primaryKey,
                    'trashKind': post.trashKind,
                    'postKind': post.postKind,
                    'author': post.author,
                    'qty': post.qty,
                    'location': post.author.region,
                    'content': post.content,
                    'created_at': str(post.created_at.strftime("%Y-%m-%d %H:%M:%S")),
                    'image': []
                }
                try:
                    postForm["image"].append(marketPostImage.objects.get(postModel=post, order=1).image)
                except ObjectDoesNotExist:
                    pass
                returnData["postList"].append(postForm)
            return JsonResponse(OK_200(data=returnData), status=200)
        try:
            post = marketPost.objects.get(primaryKey=int(pk))
            postForm = {
                'pk': post.primaryKey,
                'trashKind': post.trashKind,
                'postKind': post.postKind,
                'author': post.author,
                'qty': post.qty,
                'location': post.author.region,
                'content': post.content,
                'created_at': str(post.created_at.strftime("%Y-%m-%d %H:%M:%S")),
                'image': []
            }
            try:
                images = marketPostImage.objects.filter(postModel=post).order_by('order')
                images = list(images)
                for image in images:
                    postForm["image"].append(image.image)
            except ObjectDoesNotExist:
                pass
            returnData["postList"].append(postForm)
        except ObjectDoesNotExist:
            return JsonResponse(CUSTOM_CODE(status=404, message="There is no Exiting post", data=returnData), status=404)
        return JsonResponse(OK_200(data=returnData), status=200)


@method_decorator(csrf_exempt, name='dispatch')
class connectUser(APIView):
    def post(self, request):
        returnData = {
            "kakaoID": "",
            "openChat": "",
            "instagram": ""
        }
        try:
            pk = request.query_params['pk']
        except (KeyError, ValueError):
            return JsonResponse(BAD_REQUEST_400(message='Some Values are missing', data=returnData), status=400)
        try:
            post = marketPost.objects.get(primaryKey=int(pk))
        except ObjectDoesNotExist:
            return JsonResponse(CUSTOM_CODE(status=404, message="There is no Exiting post", data=returnData), status=404)
        userObjectData = post.author
        userObjectData = userInfo.objects.get(user=userObjectData)
        returnData["kakaoID"] = userObjectData.kakaoID
        returnData["openChat"] = userObjectData.openChat
        returnData["instagram"] = userObjectData.instagram
        return JsonResponse(OK_200(data=returnData), status=200)


@method_decorator(csrf_exempt, name='dispatch')
class artPostAPI(APIView):
    def post(self, request):
        returnData = {"pk": 0}
        if not request.user.is_authenticated or request.user.is_anonymous:
            return JsonResponse(BAD_REQUEST_400(message='Some Values are missing', data=returnData), status=400)
        try:
            title = request.data['title']
            content = request.data['content']
        except (KeyError, ValueError):
            return JsonResponse(BAD_REQUEST_400(message='Some Values are missing', data=returnData), status=400)
        artPostModel = artPost(
            content=content,
            title=title,
            author=request.user
        )
        artPostModel.save()
        returnData["pk"] = artPostModel.primaryKey
        try:
            imageList = request.FILES.getlist['image']
            imageCount = 1
            for image in imageList:
                imageModel = artPostImage(postModel=artPostModel, image=image, order=imageCount)
                imageModel.save()
                imageCount += 1
        except (KeyError, ValueError):
            pass
        return JsonResponse(OK_200(data=returnData))

    def get(self, request):
        returnData = {
            "postList": []
        }
        try:
            pk = request.query_params['pk']
        except (KeyError, ValueError):
            try:
                post_list = artPost.objects.all().order_by('created_at')
                post_list = list(post_list)
            except ObjectDoesNotExist:
                return JsonResponse(OK_200(data=returnData), status=200)
            for post in post_list:
                postForm = {
                    'pk': post.primaryKey,
                    'title': post.title,
                    'author': post.author,
                    'content': post.content,
                    'created_at': str(post.created_at.strftime("%Y-%m-%d %H:%M:%S")),
                    'image': []
                }
                try:
                    postForm["image"].append(artPostImage.objects.get(postModel=post, order=1).image)
                except ObjectDoesNotExist:
                    pass
                returnData["postList"].append(postForm)
            return JsonResponse(OK_200(data=returnData), status=200)
        try:
            post = marketPost.objects.get(primaryKey=int(pk))
            postForm = {
                'pk': post.primaryKey,
                'title': post.title,
                'author': post.author,
                'content': post.content,
                'created_at': str(post.created_at.strftime("%Y-%m-%d %H:%M:%S")),
                'image': []
            }
            try:
                images = artPostImage.objects.filter(postModel=post).order_by('order')
                images = list(images)
                for image in images:
                    postForm["image"].append(image.image)
            except ObjectDoesNotExist:
                pass
            returnData["postList"].append(postForm)
        except ObjectDoesNotExist:
            return JsonResponse(CUSTOM_CODE(status=404, message="There is no Exiting post", data=returnData), status=404)
        return JsonResponse(OK_200(data=returnData), status=200)


@method_decorator(csrf_exempt, name='dispatch')
class artPostAPI(APIView):
    def post(self, request):
        returnData = {"pk": 0}
        if not request.user.is_authenticated or request.user.is_anonymous:
            return JsonResponse(BAD_REQUEST_400(message='Some Values are missing', data=returnData), status=400)
        try:
            pk = request.data['pk']
            title = request.data['title']
            content = request.data['content']
        except (KeyError, ValueError):
            return JsonResponse(BAD_REQUEST_400(message='Some Values are missing', data=returnData), status=400)
        challengePostModel = challengePost(
            art=artPost.objects.get(primaryKey=pk),
            content=content,
            title=title,
            author=request.user
        )
        challengePostModel.save()
        returnData["pk"] = challengePostModel.primaryKey
        try:
            imageList = request.FILES.getlist['image']
            imageCount = 1
            for image in imageList:
                imageModel = challengePostImage(postModel=challengePostModel, image=image, order=imageCount)
                imageModel.save()
                imageCount += 1
        except (KeyError, ValueError):
            pass
        return JsonResponse(OK_200(data=returnData))


    def get(self, request):
        returnData = {
            "postList": []
        }
        try:
            pk = request.query_params['pk']
        except (KeyError, ValueError):
            try:
                post_list = challengePost.objects.all().order_by('created_at')
                post_list = list(post_list)
            except ObjectDoesNotExist:
                return JsonResponse(OK_200(data=returnData), status=200)
            for post in post_list:
                postForm = {
                    'pk': post.primaryKey,
                    'title': post.title,
                    'author': post.author,
                    'content': post.content,
                    'authorship_pk': post.art.author,
                    'created_at': str(post.created_at.strftime("%Y-%m-%d %H:%M:%S")),
                    'image': []
                }
                try:
                    postForm["image"].append(artPostImage.objects.get(postModel=post, order=1).image)
                except ObjectDoesNotExist:
                    pass
                returnData["postList"].append(postForm)
            return JsonResponse(OK_200(data=returnData), status=200)
        try:
            post = marketPost.objects.get(primaryKey=int(pk))
            postForm = {
                'pk': post.primaryKey,
                'title': post.title,
                'author': post.author,
                'content': post.content,
                'created_at': str(post.created_at.strftime("%Y-%m-%d %H:%M:%S")),
                'image': []
            }
            try:
                images = artPostImage.objects.filter(postModel=post).order_by('order')
                images = list(images)
                for image in images:
                    postForm["image"].append(image.image)
            except ObjectDoesNotExist:
                pass
            returnData["postList"].append(postForm)
        except ObjectDoesNotExist:
            return JsonResponse(CUSTOM_CODE(status=404, message="There is no Exiting post", data=returnData), status=404)
        return JsonResponse(OK_200(data=returnData), status=200)
