
import obspy
import os
import uuid
import pyrotd

from apiview.models import *
from apiview.serializer import *

from django.contrib.auth.models import Group, User
from django.shortcuts import render

from obspy import Stream, Trace, UTCDateTime, read_inventory

from rest_framework import permissions, viewsets, authentication, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.permissions import IsAuthenticated, IsAdminUser

import validators
# Create your views here.

# class UploadView(viewsets.ModelViewSet):
#     queryset = UploadFile.objects.all()
#     serializer_class = FileUploadSerializer
   
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def upload_file(request):
    
    if request.method == 'GET':       
       dd = ''
    elif request.method == 'POST':
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
        else:
            uploaded_file = None

        data_str = request.data.get('string_data', '')

        try:
            if uploaded_file:
                file = UploadFile(file=uploaded_file)
                file.save()
                serializer = FileUploadSerializer(file)
                file_url = request.build_absolute_uri(serializer.data['file'])
                return Response({
                    'file ': file_url,
                    'string_data ': ''
                    }, status=status.HTTP_201_CREATED)
            
            elif data_str:
                if validators.url(data_str):
                    url = UploadFile(string_data=data_str)
                    url.save()
                    serializer = FileUploadSerializer(url)
                    string_url = request.build_absolute_uri(serializer.data['string_data'])
                    return Response({
                        'file ': '',
                        'string_data ': string_url
                        }, status=status.HTTP_201_CREATED)
                else:
                    raise ValidationError('No es Valido')                     
            else:
                raise ValidationError('No se proporcionaron datos')
        except Exception as e:
            return Response({'error': 'Verificar Datos'}, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def station_data(request):
    
    if request.method == 'GET':       
       dd = ''
    elif request.method == 'POST':
        data_str = request.data.get('data')

        if not data_str:
            raise APIException('No se proporcionó datos para Lectura')
        try:
            sts = obspy.read(data_str)
            sts.merge(method=1, fill_value= 'latest')
            tr_info = extract_tr_info(sts)
            inventory = read_inventory_safe(data_str)
            combined_info = combine_tr_and_inv_info(tr_info, inventory)
            #seismic_record_instance = SeismicData(data=combined_info)            
            return Response({'data' : combined_info}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'Error => {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

def extract_tr_info(sts):
        tr_info = []
        for tr in sts:
            tr_info.append({
                'network': tr.stats.network,
                'station': tr.stats.station,
                'location': tr.stats.location,
                'channel': tr.stats.channel,
                'starttime': str(tr.stats.starttime),
                'endtime': str(tr.stats.endtime),
                'sampling_rate': tr.stats.sampling_rate,
                'delta': tr.stats.delta,
                'npts': tr.stats.npts,
                'calib': tr.stats.calib,
                'format': tr.stats._format,
            })
        return tr_info

def read_inventory_safe(data_str):
    try:
        return read_inventory(data_str)
    except Exception:
        return None

def combine_tr_and_inv_info(tr_info, inventory):
    combined_info = tr_info
    if inventory:
        inv_info = []
        for network in inventory:
            for station in network:
                for channel in station:
                    inv_info.append({
                        'network': network.code,
                        'station': station.code,
                        'location': channel.location_code,
                        'f_calib': channel.response.instrument_sensitivity.value,
                        'und_calib': channel.response.instrument_sensitivity.input_units 
                    })
        combined_info = []
        for tr_item in tr_info:
            for inv_item in inv_info:
                if (tr_item['network'] == inv_item['network'] and
                    tr_item['station'] == inv_item['station'] and
                    tr_item['location'] == inv_item['location']):
                    combined_info.append({**tr_item, **inv_item})
                    break
    return combined_info

