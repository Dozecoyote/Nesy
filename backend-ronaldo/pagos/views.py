from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import TransactionSerializer
from .models import Transaction, Balance, Users
import stripe
from django.db.models import Q
from .signals import signal_transferencia
# import base64
# import numpy as np
# import cv2
# import face_recognition
# import requests
# from PIL import Image
# import io
# import os

stripe.api_key = 'sk_test_51P0IeWP9Ot3ecyAmM9aCRnphdEMkJJoLtlHaomOPghHWr8Pt35fH74cCqFN5jYPXYFXNmUphODU0m8tHzVorVm0s00lMeZ1qwy'

endpoint_secret = 'whsec_O7kbRNMRJZm2WmAgOfSxux0KHZVjCwbi'

class StripeUsuario(APIView):

        def post(self, request):

            data = request.data
            metadata = {
                "user_id": data['id'],
                "type_id_id": 2,
                "amount": data['cantidad']
            }

            if data['mode'] == "mobile":

                try:
                    paymentIntent = stripe.PaymentIntent.create(
                        amount=data['cantidad']*100,
                        currency='mxn',
                        payment_method_types=["oxxo", "card"],
                        metadata=metadata
                    )
                except:
                    return Response({
                        "message":"Error en la peticion"
                    })
                
                return Response({
                    "clientSecret":paymentIntent['client_secret']
                })

            try:
                    res = stripe.checkout.Session.create(
                        payment_method_types=['card', 'oxxo'],
                        # The parameter is optional. The default value of expires_after_days is 3.
                        payment_method_options={
                            'oxxo' : {
                            'expires_after_days': 2
                            }
                        },
                        line_items=[
                            {
                            "price_data": {
                                "currency": "mxn",
                                "product_data": {"name": 1},
                                "unit_amount": data['cantidad']*100,
                            },
                            "quantity": 1,
                            },
                        ],
                        metadata=metadata,
                        mode="payment",
                        success_url="http://localhost:4242/success.html",
                        cancel_url="http://localhost:4242/cancel.html",
                    )
            except:
                return Response(
                    {
                        'message' : 'Error en el servidor'
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response(
                {
                    'data':res
                },
                status=status.HTTP_200_OK
            )

class Wallet(APIView):

    def get(self, request, id):
        
        try:
            data = Balance.objects.get(user_id = id)
        except Balance.DoesNotExist:
            return Response({"message": "no existe el usuario"})

        return Response({"cantidad": data.balance})

class StripeChofer(APIView):

    def post(self, request):

        user_id = request.data['user_id']

        if user_id is None:
            return Response({"message": "el parametro user_id es requrido"})

        try:
            connect = stripe.Account.create(type="express")

            link = stripe.AccountLink.create(
                account= connect['id'],
                refresh_url="https://example.com/reauth",
                return_url="https://example.com/return",
                type="account_onboarding",
            )

        except stripe.error.StripeError as e:
            
            print(f"Stripe error: {e.user_message}")
            return Response({"message": "Ocurrió un error con el servicio de Stripe"})
        
        except Exception as e:
            # Log unexpected errors
            print(f"Unexpected error: {str(e)}")
            return Response({"message": "Ocurrió un error inesperado"})

        try:
            user = Users.objects.get(id = user_id)
        except Users.DoesNotExist:
            return Response({
            "message": "No existe el usuario"
        })

        try:
            user.stripe = connect['id']
            user.save()
        except:
            return Response({
            "message": "Ocurrio un problema al vincular el usuario con stripe"
        })


        return Response({
            "message": "se conecto el usuario a stripe con exito",
            "url" : link.url
        })

class Chofer(APIView):

    def put(self, reuqest, id):

        try:
            user = Users.objects.get(id = id)
        except Users.DoesNotExist:
            return Response({
            "message": "No existe el usuario"
        })

        if user.stripe == None:
            return Response({
            "message": "El usuario no es chofer"
        })

        try:
            link = stripe.AccountLink.create(
                account= user.stripe,
                refresh_url="https://example.com/reauth",
                return_url="https://example.com/return",
                type="account_onboarding",
            )

        except stripe.error.StripeError as e:
            
            print(f"Stripe error: {e.user_message}")
            return Response({"message": "Ocurrió un error con el servicio de Stripe"})
        
        except Exception as e:
            # Log unexpected errors
            print(f"Unexpected error: {str(e)}")
            return Response({"message": "Ocurrió un error inesperado"})

        return Response({
            "message": "se obtuvo el url para actualizar los datos",
            "url" : link.url
        })
    
    def get(self, request, id):

        try:
            chofer = Users.objects.get(id = id)
        except Users.DoesNotExist:
            return Response(
            {
                "message":"No existe el usuario"
            }
        )

        stripe_chofer = stripe.Account.retrieve(chofer.stripe)

        if stripe_chofer.details_submitted == False:
            return Response(
            {
                "message":"Falta ingresar los datos"
            }
        )

        data_chofer = stripe.Balance.retrieve(stripe_account=chofer.stripe)

        try:
            # List balance transactions for the connected Stripe account
            transactions = stripe.BalanceTransaction.list(
                stripe_account=chofer.stripe,
                limit=10  # Adjust limit as needed
            )
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e.user_message}")
            return Response({"message": "Ocurrió un error con el servicio de Stripe"}, status=500)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return Response({"message": "Ocurrió un error inesperado"}, status=500)


        return Response(
            {
                "message":"ok",
                "data": data_chofer,
                "transacciones": transactions
            }
        )

class Webhooks(APIView):

    def post(self, request):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            # Invalid payload.
            return Response(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid Signature.
            return Response(status=400)

        # Manejar el evento
        if event['type'] == "payment_intent.succeeded":
            session = event['data']['object']

            if not session['metadata']:
                return    

            session['metadata']['status'] = "X"

            serializer = TransactionSerializer(data=session['metadata'])  

            if serializer.is_valid():
                    serializer.save()
                    print('datos guardados')

            else:
                print("Errores de validación:", serializer.errors)

        if event['type'] == 'checkout.session.completed':

            session = event['data']['object']
            session['metadata']['status'] = "X"
            print("Datos del metadata:", session['metadata'])

            serializer = TransactionSerializer(data=session['metadata'])  

            if serializer.is_valid():
                # Confirmar que el pago fue exitoso
                payment_intent_id = session.get('payment_intent')
                payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                print("Datos después de la conversión:", serializer.validated_data)

                if payment_intent['status'] == 'succeeded':
                    # Lógica para manejar la metadata y actualizar la base de datos
                    serializer.save()

                    print('datos guardados')

            else:
                print("Errores de validación:", serializer.errors)
                    

        elif event['type'] == 'payment_intent.payment_failed':

            session = event['data']['object']
            session['metadata']['status'] = "E"

            print(session['metadata'])

            serializer = TransactionSerializer(data=session['metadata'])  

            if serializer.is_valid():
                # Confirmar que el pago fue exitoso
                payment_intent_id = session.get('payment_intent')
                payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

                if payment_intent['status'] == 'succeeded':
                    # Lógica para manejar la metadata y actualizar la base de datos
                    serializer.save()

                    print('datos guardados')

            else:
                print('datos incorrectos')

        else:
            # Tipo de evento inesperado
            print(f'Unhandled event type {event["type"]}')

        return Response({'status': 'success'}, status=200)
    
class Pagos(APIView):

    def post(self, request):

        # balance = stripe.Balance.retrieve()
        # print(balance)

        user_id = request.data['user_id']
        chofer_id = request.data['chofer_id']
        cantidad = request.data['cantidad']

        try:
            user = Balance.objects.get(user_id = user_id)
        except Balance.DoesNotExist:
            return Response(
            {
                "message": "No existe el usuario"
            }
        )

        try:
            chofer = Users.objects.get(id = chofer_id)
            if chofer.stripe is None:
                return Response(
                    {
                        "message": "No es una cuenta de chofer"
                    }
                )
        except Balance.DoesNotExist:
            return Response(
            {
                "message": "No existe el chofer"
            }
        )


        if user.balance >= 12:
            
            pago = {
                "user_id": user_id,
                "amount": cantidad,
                "type_id": 1
            }

            serializer = TransactionSerializer(data=pago)

            if serializer.is_valid():

                try:
                    stripe.Transfer.create(
                        amount=pago['amount']*100,
                        currency="mxn",
                        destination=chofer.stripe,
                    )
                except:
                    return Response({
                    "message": "error al transferir a la cuenta conectada con stripe"
                })

                serializer.save()
            else:
                return Response({
                    "message": serializer.errors
                })
            
            
        else:
            return Response({
                "message": "no hay suficientes tokens"
            })



        return Response(
            {
                "message": "exitoso"
            }
        )

class Transferencias(APIView):

    def post(self, request):
        
        user_id = request.data['user_id']
        cantidad = request.data['cantidad']
        trans_id = request.data['trans_id']

        try:
            user = Balance.objects.get(user_id=user_id)
        except Balance.DoesNotExist:
            return Response(
                {
                    "message": "El usuario no existe"
                }
            )

        trans_id = Users.objects.filter(Q(curp=trans_id) | Q(email=trans_id)).values('id')

        if not trans_id.exists():
            return Response(
                {
                    "message": "El usuario a tranferir no existe"
                }
            )
        
        user_trans = Balance.objects.get(user_id=trans_id[0]['id'])

        print(user_trans.__dict__)


        if user.balance >= cantidad:

            transferencia = {
                "user_id": user_id,
                "amount": cantidad,
                "type_id_id": 4,
                "user_trans_id": trans_id[0]['id']
            }

            serializer = TransactionSerializer(data=transferencia) 

            if serializer.is_valid():
                serializer.save()
            else:
               return Response(
                   {
                       "message": serializer.errors
                   }
               ) 
        
            signal_transferencia.send(sender=self.__class__, data={ "usuario":user_trans, "cantidad":cantidad })
            
        else:
            return Response(
                {
                   "message": "tokens insuficientes"
                }
            ) 

        return Response(
            {
                "message": "se realizo con exito"
            }
        )

class Transferencia(APIView):

    def get(self, request, id):

        record = Transaction.objects.filter(user_id = id)
        
        serialaizer = TransactionSerializer(record, many=True)

        return Response(
            {
                "data": serialaizer.data
            }
        )

# class ValidarImagenes(APIView):

#     def get(self, request, id):

#         response = requests.get(f'http://159.54.149.151:8080/api/users/get/user/{id}')
#         response.raise_for_status()  # Lanza un error si la solicitud falla
#         datos = response.json()  # Asume que la respuesta es JSON

        
#         def load_and_convert_image(image_path):
#             # Cargar la imagen con OpenCV
#             image_bgr = cv2.imread(image_path)
            
#             if image_bgr is None:
#                 raise ValueError(f"No se pudo cargar la imagen desde {image_path}. Verifica la ruta y el archivo.")
            
#             # Convertir la imagen BGR a RGB
#             image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            
#             return image_rgb

#         # Decodificar la cadena Base64
#         photo = base64.b64decode(datos['photo'])
#         ine = base64.b64decode(datos['ine'])

#         # Crear un objeto de imagen desde los datos binarios
#         image_photo = Image.open(io.BytesIO(photo))
#         image_ine = Image.open(io.BytesIO(ine))

#         image_ine = image_ine.convert("L")
#         image_photo = image_photo.convert("L")

#         image_photo.save("imagen_decodificada.png")
#         image_ine.save("imagen_decodificada2.png")
        
#         # Cargar y convertir las imágenes
#         photo_convert = load_and_convert_image("imagen_decodificada.png")
#         ine_convert = load_and_convert_image("imagen_decodificada.png")

#         rostros_imagen_1 = face_recognition.face_encodings(photo_convert)
#         rostros_imagen_2 = face_recognition.face_encodings(ine_convert)

#         if len(rostros_imagen_1) > 0 and len(rostros_imagen_2) > 0:
#             rostro_1 = rostros_imagen_1[0]
#             rostro_2 = rostros_imagen_2[0]
            
#             # Comparar los rostros
#             resultados = face_recognition.compare_faces([rostro_1], rostro_2)
            
#             if resultados[0]:
#                 print("Los rostros son de la misma persona.")
#             else:
#                 print("Los rostros no son de la misma persona.")
#         else:
#             print("No se encontraron rostros en una o ambas imágenes.")

#         os.remove("imagen_decodificada.png")
#         os.remove("imagen_decodificada2.png")

#         return Response({
#             "message":resultados
#         })

class ObtenerContactos(APIView):

    def get(self, request, id):
        try:
            # Obtener los user_trans_ids únicos
            user_trans_ids = Transaction.objects.filter(
                user_id=id, user_trans_id__isnull=False
            ).values_list('user_trans_id', flat=True).distinct()

            # Asegurarse de que el conjunto de IDs no esté vacío
            if not user_trans_ids:
                return Response(
                    {"message": "No se encontraron transacciones para el usuario especificado."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Obtener la información de los usuarios basados en los user_trans_ids
            usuarios = Users.objects.filter(id__in=user_trans_ids)
            data = list(usuarios.values('curp', 'email', 'name', 'surnames'))  # ajusta los campos según tus necesidades

        except Users.DoesNotExist:
            return Response(
                {"message": "No se encontraron usuarios para los IDs especificados."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": f"Ocurrió un error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(
            {
                "message": "éxito",
                "data": data
            },
            status=status.HTTP_200_OK
        )