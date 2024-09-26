from django.shortcuts import render
from django.core.mail import send_mail
from django.urls import reverse
from organization.serializers import OrganizationSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_protect
from rest_framework import status
from organization.models import Organization
from django.conf import settings
from authlib.integrations.django_client import OAuth
from urllib.parse import urlencode
from django.shortcuts import redirect


oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)


# @csrf_protect
# @api_view(['POST'])
# def create_organization(request):
#     serializer = OrganizationSerializer(data=request.data)

#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     else:
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_organization(request):
    serializer = OrganizationSerializer(data=request.data)

    if serializer.is_valid():
        organization = serializer.save()

        # Construct the password setup link
        setup_link = request.build_absolute_uri(reverse('password_setup', kwargs={'pk': organization.pk}))

        # Send the email
        send_mail(
            'Setup Your Password',
            f'Hi {organization.name},\n\nPlease click the link below to set up your password:\n{setup_link}',
            settings.EMAIL_HOST_USER,
            [organization.email],
            fail_silently=False,
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_organization(request, pk):
    organization = Organization.objects.get(pk=pk)
    serializer = OrganizationSerializer(organization)
    
    return Response(serializer.data)

@api_view(['POST'])
def password_setup(request, pk):
    organization = Organization.objects.get(pk=pk)

    # Logic to handle password setup (you might want to validate a token)
    # For example, you could use a token or any validation mechanism
    # that confirms this is a valid password reset request.

    # After successful validation, you can set the password.
    organization.set_password(request.data['password'])  # Use DRF's serializers for better validation.
    organization.save()

    return Response({"message": "Password has been set successfully."}, status=status.HTTP_200_OK)

   
    
import requests
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.response import Response

def auth_callback(request):
    # Get the authorization code from the query parameters
    code = request.GET.get('code')
    
    # Exchange the authorization code for tokens
    token_url = f'https://{settings.AUTH0_DOMAIN}/oauth/token'
    token_payload = {
        'grant_type': 'authorization_code',
        'client_id': settings.AUTH0_CLIENT_ID,
        'client_secret': settings.AUTH0_CLIENT_SECRET,
        'code': code,
        'redirect_uri': 'http://localhost:8000/auth/callback',
    }

    token_response = requests.post(token_url, json=token_payload)
    tokens = token_response.json()

    # At this point, you have tokens including access and ID tokens
    # Process or store the tokens as needed (e.g., create or update user session)
    
    return Response(tokens)




@api_view(['GET', 'POST'])
def login(request):
    # Parameters for Auth0 authorization endpoint
    params = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'response_type': 'code',  # Use 'code' for Authorization Code Flow
        'redirect_uri': 'http://localhost:8000/auth/callback',  # Replace with your callback URL
        'scope': 'openid profile email',  # Scope includes openid, profile, and email
        'audience': settings.AUTH0_AUDIENCE,  # Optional, include audience for API access
    }
    
    # Redirect the user to Auth0's /authorize endpoint
    auth0_url = f'https://{settings.AUTH0_DOMAIN}/authorize?' + urlencode(params)
    return redirect(auth0_url)


@api_view(['POST'])
def logout(request):
    # Invalidate the user's session on Auth0
    return Response(
        {
            "logout_url": f"https://{AUTH0_DOMAIN}/v2/logout?client_id={CLIENT_ID}&returnTo={REDIRECT_URI}"
        },
        status=status.HTTP_200_OK
    )
    
    
    
@api_view(['GET'])
def callback(request):
    code = request.GET.get('code')
    if not code:
        return Response({"error": "No code provided"}, status=400)

    # Exchange code for access token
    token_url = f'https://{settings.AUTH0_DOMAIN}/oauth/token'
    token_payload = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'client_secret': settings.AUTH0_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': f'http://localhost:8000/auth/callback',  # Ensure this matches your Auth0 settings
    }
    
    token_response = requests.post(token_url, json=token_payload)
    token_json = token_response.json()

    access_token = token_json.get('access_token')
    
    # Use the access token to get user info
    user_info_url = f'https://{settings.AUTH0_DOMAIN}/userinfo'
    user_info_response = requests.get(user_info_url, headers={'Authorization': f'Bearer {access_token}'})
    user_info = user_info_response.json()

    email = user_info.get('email')
    name = user_info.get('name')
    auth0_user_id = user_info.get('sub')  # Extract the user ID from the user info

    # Check if organization exists; if not, create it
    organization, created = Organization.objects.get_or_create(
        auth0_user_id=auth0_user_id,  # Use auth0_user_id for lookups
        defaults={'email': email, 'name': name}
    )

    # Optionally update the organization if it exists
    if not created:
        organization.name = name
        organization.email = email
        organization.save()

    # Check if organization exists; if not, create it
    organization, created = Organization.objects.get_or_create(email=email, defaults={'name': name})

    return Response({"access_token": access_token, "organization": organization.name}, status=200)