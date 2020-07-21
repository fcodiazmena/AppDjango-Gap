from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.db.models import Q, F
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from encuesta.models import Dominio, Subdominio, Pregunta, Respuesta, Usuario, Empresa
from encuesta.forms import EmpresaForm, UsuarioForm

import json

import re

def index(request):
    context = {}
    template_name = 'encuesta/index.html'
    if request.method == "GET":
        if request.user.usuario.administrador == True:
            empresas = list(Empresa.objects.exclude(id=request.user.usuario.empresa.id).values('id', 'nombre'))
            context['empresas'] = empresas
        else:
            id_empresa = request.user.usuario.empresa.id
            datos = list(Subdominio.objects.select_related('dominio').annotate(dominio_nombre=F('dominio__nombre')).filter(dominio__empresa=id_empresa).values('id', 'nombre', 'dominio_id', 'dominio_nombre'))
            # dominios = Dominio.objects.filter(empresa=id_empresa)
            # context['dominios'] = dominios
            dominios = []

            objeto = {}
            objeto2 = {}
            subdominios = []

            no_existe = True

            for i in datos:
                no_existe = True
                print(i['nombre'])
                if len(dominios) == 0:
                    print('add')
                    objeto['nombre'] = i['dominio_nombre']
                    objeto['id'] = i['dominio_id']
                    objeto2['id'] = i['id']
                    objeto2['nombre'] = i['nombre']
                    objeto['subdominios'] = [objeto2]
                    dominios.append(objeto)
                    objeto = {}
                    objeto2 = {}
                else:
                    for d in dominios:
                        if d['nombre'] == i['dominio_nombre']:
                            # existe el objeto
                            print('add')
                            objeto2['id'] = i['id']
                            objeto2['nombre'] = i['nombre']
                            d['subdominios'].append(objeto2)
                            objeto2 = {}
                            no_existe = False

                    if no_existe == True:
                        print('create')
                        objeto['nombre'] = i['dominio_nombre']
                        objeto['id'] = i['dominio_id']
                        objeto2['id'] = i['id']
                        objeto2['nombre'] = i['nombre']
                        objeto['subdominios'] = [objeto2]
                        dominios.append(objeto)
                        objeto = {}
                        objeto2 = {}

            context['dominios'] = dominios
            print(dominios)

    return render(request, template_name, context)


def subdominio_list(request, id_dominio, id_subdominio):
    context = {}
    template_name = 'encuesta/subdominio_list.html'

    if request.method == 'GET':
        id_empresa = request.user.usuario.empresa.id
        datos = list(Subdominio.objects.select_related('dominio').annotate(dominio_nombre=F('dominio__nombre')).filter(dominio__empresa=id_empresa).values('id', 'nombre', 'dominio_id', 'dominio_nombre'))
        dominios = []

        objeto = {}
        objeto2 = {}
        subdominios = []

        no_existe = True

        for i in datos:
            no_existe = True
            print(i['nombre'])
            if len(dominios) == 0:
                print('add')
                objeto['nombre'] = i['dominio_nombre']
                objeto['id'] = i['dominio_id']
                objeto2['id'] = i['id']
                objeto2['nombre'] = i['nombre']
                objeto['subdominios'] = [objeto2]
                dominios.append(objeto)
                objeto = {}
                objeto2 = {}
            else:
                for d in dominios:
                    if d['nombre'] == i['dominio_nombre']:
                        # existe el objeto
                        print('add')
                        objeto2['id'] = i['id']
                        objeto2['nombre'] = i['nombre']
                        d['subdominios'].append(objeto2)
                        objeto2 = {}
                        no_existe = False

                if no_existe == True:
                    print('create')
                    objeto['nombre'] = i['dominio_nombre']
                    objeto['id'] = i['dominio_id']
                    objeto2['id'] = i['id']
                    objeto2['nombre'] = i['nombre']
                    objeto['subdominios'] = [objeto2]
                    dominios.append(objeto)
                    objeto = {}
                    objeto2 = {}

        context['dominios'] = dominios
        print(dominios)

        subdominio = Subdominio.objects.get(id=id_subdominio)
        context['subdominio'] = subdominio
        preguntas = Pregunta.objects.filter(Q(subdominio=id_subdominio) & Q(subdominio__dominio=id_dominio) & Q(usuario=request.user.usuario.id))
        context['preguntas'] = preguntas

        # Verificando las preguntas ya respondidas
        respondida = {}
        for pregunta in preguntas:
            try:
                respuesta = Respuesta.objects.get(pregunta=pregunta.id)
                respondida[pregunta.id] = respuesta.voto
            except Respuesta.DoesNotExist:
                pass
        context['respondida'] = respondida
    elif request.method == 'POST':
        print(request.POST)
        # Validar si el post viene vacio

        # Almacenando indices de post y de pregunta
        indices_post = []
        indices_pregunta = []
        for indice in request.POST:
            if indice != 'csrfmiddlewaretoken':
                indices_post.append(indice)
                indices_pregunta.append(indice[6:])

        # Verificando las preguntas que fueron enviadas si tienen respuesta
        for indice_pregunta, indice_post in zip(indices_pregunta, indices_post):
            try:
                respuesta = Respuesta.objects.get(pregunta=indice_pregunta)
            except Respuesta.DoesNotExist:
                pregunta = Pregunta.objects.get(id=indice_pregunta)
                respuesta = Respuesta(pregunta=pregunta, voto=request.POST.get(indice_post))
                respuesta.save()

        # Redireccionar al inicio
        return HttpResponseRedirect(reverse('index'))

    return render(request, template_name, context)

def pregunta_list(request, id_dominio):
    context = {}
    template_name = 'encuesta/pregunta_list.html'

    if request.method == 'GET':
        id_empresa = request.user.usuario.empresa.id
        datos = list(Subdominio.objects.select_related('dominio').annotate(dominio_nombre=F('dominio__nombre')).filter(dominio__empresa=id_empresa).values('id', 'nombre', 'dominio_id', 'dominio_nombre'))
        dominios = []

        objeto = {}
        objeto2 = {}

        no_existe = True

        for i in datos:
            no_existe = True
            if len(dominios) == 0:
                objeto['nombre'] = i['dominio_nombre']
                objeto['id'] = i['dominio_id']
                objeto2['id'] = i['id']
                objeto2['nombre'] = i['nombre']
                objeto['subdominios'] = [objeto2]
                dominios.append(objeto)
                objeto = {}
                objeto2 = {}
            else:
                for d in dominios:
                    if d['nombre'] == i['dominio_nombre']:
                        # existe el objeto
                        objeto2['id'] = i['id']
                        objeto2['nombre'] = i['nombre']
                        d['subdominios'].append(objeto2)
                        objeto2 = {}
                        no_existe = False

                if no_existe == True:
                    objeto['nombre'] = i['dominio_nombre']
                    objeto['id'] = i['dominio_id']
                    objeto2['id'] = i['id']
                    objeto2['nombre'] = i['nombre']
                    objeto['subdominios'] = [objeto2]
                    dominios.append(objeto)
                    objeto = {}
                    objeto2 = {}

        context['dominios'] = dominios


        # Capturando todas las preguntas dependiendo del dominio y subdominio
        subdominios = []
        objeto_subdominio = {}
        datos_subdominio = Subdominio.objects.filter(dominio=id_dominio)
        for subdom in datos_subdominio:
            objeto_subdominio['nombre'] = subdom.nombre
            objeto_subdominio['id'] = subdom.id
            objeto_subdominio['preguntas'] = list(subdom.pregunta_set.filter(usuario=request.user.usuario.id))
            subdominios.append(objeto_subdominio)
            objeto_subdominio = {}
            #preguntas[subdom.id] = subdom.pregunta_set.filter(usuario=request.user.usuario.id)
        #context['preguntas'] = preguntas # diccionario de preguntas, llave id subdominio, value preguntas
        context['subdominios'] = subdominios

        # Verificando las preguntas ya respondidas
        respondida = {}
        for subdom in subdominios:
            for pregunta in subdom['preguntas']:
                try:
                    respuesta = Respuesta.objects.get(pregunta=pregunta.id)
                    respondida[pregunta.id] = respuesta.voto
                except Respuesta.DoesNotExist:
                    pass
        print(respondida)
        context['respondida'] = respondida

    elif request.method == 'POST':
        # Validar si el post viene vacio

        # Almacenando indices de post y de pregunta
        indices_post = []
        indices_pregunta = []
        for indice in request.POST:
            if indice != 'csrfmiddlewaretoken':
                indices_post.append(indice)
                indices_pregunta.append(indice[6:])

        # Verificando las preguntas que fueron enviadas si tienen respuesta
        for indice_pregunta, indice_post in zip(indices_pregunta, indices_post):
            try:
                respuesta = Respuesta.objects.get(pregunta=indice_pregunta)
            except Respuesta.DoesNotExist:
                pregunta = Pregunta.objects.get(id=indice_pregunta)
                respuesta = Respuesta(pregunta=pregunta, voto=request.POST.get(indice_post))
                respuesta.save()

        # Redireccionar al inicio
        return HttpResponseRedirect(reverse('index'))

    return render(request, template_name, context)


def resultado(request, id_empresa):
    context = {}
    template_name = 'encuesta/administrador/resultado.html'

    if request.method == 'GET':
        empresas = list(Empresa.objects.exclude(id=request.user.usuario.empresa.id).values('id', 'nombre'))
        context['empresas'] = empresas
        # Capturando los dominios por empresa
        dominios = Dominio.objects.filter(empresa__id=id_empresa)

        lista_dominios = list(dominios)
        doms = []
        doms_objeto = {}
        
        # Capturando datos, nombre del dominio, total de preguntas, cantidad de verdaderas, cantidad de falsas, cantidad de no respondidas (NA)
        for dom in dominios:
            doms_objeto['Nombre'] = dom.nombre
            doms_objeto['Total'] = Pregunta.objects.filter(subdominio__dominio=dom.id).count()
            doms_objeto['Verdadero'] = Pregunta.objects.filter(Q(subdominio__dominio=dom.id) & Q(respuesta__voto="Verdadero")).count()
            doms_objeto['Falso'] = Pregunta.objects.filter(Q(subdominio__dominio=dom.id) & Q(respuesta__voto="Falso")).count()
            doms_objeto['NA'] = doms_objeto['Total'] - (doms_objeto['Verdadero'] + doms_objeto['Falso'])
            doms.append(doms_objeto)
            doms_objeto = {}
        
        # Transformando a JSON para manipulacion en el Template
        context['data'] = json.dumps(doms)
    elif request.method == "POST":
        print(request.POST)
        mensaje = request.POST.get('mensaje_correo')

        email = EmailMultiAlternatives('Datos de encuesta gap', mensaje, settings.EMAIL_HOST_USER, ['franciscodiaz_97@hotmail.com'])

        email.send()

        return redirect('index')

    return render(request, template_name, context)


def usuario_list(request):
    context = {}
    template_name = 'encuesta/administrador/usuarios/usuario_list.html'

    if request.method == 'GET':
        empresas = list(Empresa.objects.exclude(id=request.user.usuario.empresa.id).values('id', 'nombre'))
        context['empresas'] = empresas
        usuarios = Usuario.objects.select_related('user').all()
        context['usuarios'] = usuarios

    
    return render(request, template_name, context)


def usuario_add(request):
    context = {}
    template_name = 'encuesta/administrador/usuarios/usuario_add.html'

    if request.method == 'GET':
        empresas = list(Empresa.objects.exclude(id=request.user.usuario.empresa.id).values('id', 'nombre'))
        context['empresas'] = empresas
        form = EmpresaForm()
        context['form'] = form
    elif request.method == 'POST':  
        print(request.POST)
        form = EmpresaForm(request.POST)
        context['form'] = form
        nombre = request.POST.get('nombre')
        if nombre.isalpha():
            print('nombre valido')
        else:
            print("nombre invalido")
            context['msg_error'] = 'Nombre invalido'
            return render(request, template_name, context)
            
        apellido = request.POST.get('apellido')
        if apellido.isalpha():
            print('apellido valido')
        else:
            print('apellido invalido')
            context['msg_error'] = 'Apellido invalido'
            return render(request, template_name, context)


        username = request.POST.get('username')
        resultado = Usuario.objects.filter(user__username__iexact=username).exists()

        if resultado:
            context['msg_error'] = 'Nombre de usuario, ya utilizado'
            return render(request, template_name, context)

        email = request.POST.get('email')
        if re.search(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', email):
            # valid
            print('email valido')
        else:
            print('email invalido')
            context['msg_error'] = 'Email invalido'
            return render(request, template_name, context)
                # no valid
            
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        if re.match(r'^(?=.*\d)(?=.*[a-zA-Z]).{8,20}$', password):

            if re.match(r'^(?=.*\d)(?=.*[a-zA-Z]).{8,20}$', confirm_password):

                if password != confirm_password:
                    context['msg_error'] = 'Las contraseñas no coinciden'
                    return render(request, template_name, context)

            else:
                print('pass confirm invalido')
                context['msg_error'] = 'Contraseña invalida'
                return render(request, template_name, context)
        else:
            print('pass invalido')
            context['msg_error'] = 'Contraseña invalida'
            return render(request, template_name, context)
            
        if 'admin' not in request.POST:
            admin = False
        else:
            admin = request.POST.get('admin')
            
        if form.is_valid():
            print('empresa valido')
            empresa = Empresa.objects.get(id=int(request.POST.get('empresa')))

        
        nuevo_usuario = User.objects.create_user(username, email, password)
        nuevo_usuario.first_name = nombre
        nuevo_usuario.last_name = apellido
        nuevo_usuario.save()
        nuevo_perfil = Usuario(user=nuevo_usuario, empresa=empresa, administrador=admin)
        nuevo_perfil.save()

        preguntas = [
            {
                'subdominio': 'Documento politica seguridad informatica',
                'preguntas': ['Existe una Política de Seguridad Informática la cual ha sido aprobada por la Gerencia, publicada y comunicada a todos los empleados?', 'La Politica establece el compromiso de la Gerencia y el acercamiento organizacional a la administración de seguridad informática?']
            },
            {
                'subdominio': 'Revision de politica seguridad informatica',
                'preguntas': ['Si la Política de Seguridad Informática es revisada en intervalos programados, o si cambios significativos ocurren para asegurarse su continuidad, adecuación y efectividad.', 'Si la Política de Seguridad Informática tiene un dueño, el cual tiene responsabilidad aprobada para desarrollar, revisar y evaluar la Política de Seguridad.', 'Si existe un procedimiento definido para la revisión de la Política de Seguridad Informática y si incluye requisitos para la revisión por la Gerencia.', 'Si se toman en cuenta los resultados de las revisiones gerenciales.', 'Si se obtiene la aprobación de la gerencia para la Política revisada.']
            },
            {
                'subdominio': 'Compromiso gerencial a la seguridad informatica',
                'preguntas': ['Si la gerencia demuestra un apoyo activo a las medidas de seguridad dentro de la organización.']
            },
            {
                'subdominio': 'Coordinacion seguridad informatica',
                'preguntas': ['Si actividades relacionadas con la Seguridad Informática son coordinadas por representantes de diversas partes de la organización con roles y responsabilidades pertinentes.']
            },
            {
                'subdominio': 'Distribucion responsabilidades seguridad informatica',
                'preguntas': ['Si las responsabilidades para la protección de los activos individuales y el llevar a cabo procesos específicos de seguridad fueron definidos claramente.']
            },
            {
                'subdominio': 'Proceso autorizacion para facilidades de procesos informaticos',
                'preguntas': ['Si existe un proceso de autorización gerencial definido e implementado para cualquier nueva facilidad de proceso de información.']
            },
            {
                'subdominio': 'Acuerdos de confidencialidad',
                'preguntas': ['Si las necesidades de la organización con relación a acuerdos de confidencialidad y no divulgación (NDA) para la protección de la información han sido claramente definidos y regularmente revisados. Cubre los requisitos de proteger la confidencialidad de la información utilizando términos legales aplicables.']
            },
            {
                'subdominio': 'Contacto con autoridades',
                'preguntas': ['Si existen procedimientos que describen cuando y por quien deben ser contactadas autoridades correspondientes como ser: la Policía, Bomberos, etc. y como debe ser reportado el incidente.']
            },
            {
                'subdominio': 'Contacto con grupos de interes especial',
                'preguntas': ['Si contacto adecuado con grupos de interés especial o foros de especialistas de seguridad y asociaciones de profesionales son mantenidas.']
            },
            {
                'subdominio': 'Revision independiente de la seguridad informatica',
                'preguntas': ['Si la manera de administrar la seguridad informática y su implementación es revisada independientemente en intervalos planeados o cuando ocurren cambios mayores con relación a implementaciones de seguridad.']
            },
            {
                'subdominio': 'Identificacion de riesgos por accesos de externos',
                'preguntas': ['Si riesgos a la información de la organización y sus instalaciones operacionales, de procesos que involucran a externos o terceros ha sido identificada y controles apropiados han sido implementados antes de otorgarles acceso.']
            },
            {
                'subdominio': 'Manejando la seguridad al tratar con clientes',
                'preguntas': ['Si todos los requisitos de seguridad identificados son cumplidos antes de otorgarle acceso al cliente a la información o activos de la organización.']
            },
            {
                'subdominio': 'Manejando la seguridad en acuerdos con terceros',
                'preguntas': ['Si el acuerdo con terceros, involucrando accesos, procesos, comunicaciones o administración de la información de la organización o facilidades de proceso, o introduciendo productos o servicios a las facilidades de proceso de la información, cumple con todos los requisitos de seguridad adecuados.']
            },
            {
                'subdominio': 'Inventario de activos',
                'preguntas': ['Si todos los activos han sido identificados y un inventario o registro se mantiene con todos los activos importantes.']
            },
            {
                'subdominio': 'Dueños de activos',
                'preguntas': ['SI cada activo identificado tiene un dueño, una clasificación de seguridad definida y acordada y restricción de accesos que son revisados regularmente.']
            },
            {
                'subdominio': 'Uso aceptable de activos',
                'preguntas': ['Si regulaciones para el uso aceptable de información y activos asociados con una facilidad de proceso de la información han sido identificados, documentados e implementados.']
            },
            {
                'subdominio': 'Guia de clasificacion',
                'preguntas': ['Si la información es clasificada en términos de valor, requisitos legales, sensibilidad y criticidad para la organización.']
            },
            {
                'subdominio': 'Etiquetado y manejo de la informacion',
                'preguntas': ['Si un set de procedimientos apropiados han sido definidos para el etiquetado y manejo de la información de acuerdo con el esquema de clasificación adoptada por la organización.']
            },
            {
                'subdominio': 'Roles y responsabilidades',
                'preguntas': ['Si los roles y responsabilidades de seguridad de los empleados, contratistas y terceros fueron definidos y documentados de acuerdo con la política de seguridad informática de la organización. Fueron los roles y responsabilidades definidos y claramente comunicados a los candidatos durante el proceso previo a la contratación.']
            },
            {
                'subdominio': 'Revision antecedentes',
                'preguntas': ['Si se efectuó una revisión de antecedentes para todos los candidatos a emplear, contratistas y terceros  según regulaciones relevantes. Incluye la revisión de referencia de carácter, confirmación de calificaciones académicas como profesionales y una revisión de identidad independiente.']
            },
            {
                'subdominio': 'Terminos y condiciones de empleo',
                'preguntas': ['Si a los empleados, contratistas y terceros se les pide de firmar un Acuerdo de Confidencialidad o NO Divulgación como parte de sus acuerdos iniciales y condiciones al contrato de trabajo. Si este acuerdo cubre la responsabilidad sobre la seguridad informática de la organización y de los empleados, terceros y contratistas.']
            },
            {
                'subdominio': 'Terminos y condiciones de trabajo',
                'preguntas': ['Si los términos y condiciones de trabajo cubren las responsabilidades del empleado con relación a la seguridad informática. Donde sea apropiada, estas responsabilidades pueden continuar por un periodo determinado aun después de finalizar su contrato con la organización.']
            },
            {
                'subdominio': 'Responsabilidades administrativas',
                'preguntas': ['Si la administración requiere que los empleados, contratistas y terceros apliquen seguridad de acuerdo con políticas y procedimientos establecidos por la organización.']
            },
            {
                'subdominio': 'Concientizacion, educacion y entrenamiento sobre seguridad informatica',
                'preguntas': ['Si todos los empleados en la organización, y donde sea relevante, contratistas y terceros reciben entrenamiento adecuado de seguridad como también actualizaciones regulares en las políticas y procedimientos organizacionales correspondiente a su funciones.']
            },
            {
                'subdominio': 'Proceso disciplinario',
                'preguntas': ['Si existe un proceso disciplinario formal para los empleados que han cometido una falta en seguridad.']
            },
            {
                'subdominio': 'Responsabilidades de termino',
                'preguntas': ['Si las responsabilidades para efectuar la terminación o cambio laboral están claramente definidas y asignadas.']
            },
            {
                'subdominio': 'Devolucion de activos',
                'preguntas': ['Si existe un proceso que asegure que todos los empleados, contratistas y terceros hagan entrega de los activos de la organización bajo su control al terminar su relación laboral, contrato o acuerdo.']
            },
            {
                'subdominio': 'Eliminacion de derechos de acceso',
                'preguntas': ['Si los derechos de acceso de todos los empleados, contratistas y terceros a informaciones o facilidades informáticas, serán eliminados al termino de su relación laboral, contrato o acuerdo o será ajustado en caso de cambios.']
            },
            {
                'subdominio': 'Perimetro seguridad fisica',
                'preguntas': ['Que facilidad de seguridad física ha sido implementado para proteger el servicio de procesamiento informático. Ejemplos de tales facilidades de seguridad son control de acceso por tarjetas, paredes, recepcionista, etc.']
            },
            {
                'subdominio': 'Controles de ingreso fisico',
                'preguntas': ['Que controles de acceso existen para solo permitir el ingreso de personal autorizado dentro de varias áreas de la organización.']
            },
            {
                'subdominio': 'Asegurar oficinas, cuartos y facilidades',
                'preguntas': ['Si los cuartos que contiene los servicios de procesamientos informáticos están cerrados o contiene gabinetes o cajas de seguridad cerradas.']
            },
            {
                'subdominio': 'Protegiendo contra amenazas externas y ambientales',
                'preguntas': ['Si la protección física contra daños de fuego, inundaciones, terremotos, explosiones, disturbios civiles y otras formas de desastres ya sean naturales o causados por el hombre deben ser diseñados y aplicados.', 'Si existen potenciales amenazas de predios aledaños.']
            },
            {
                'subdominio': 'Trabajando en areas seguras',
                'preguntas': ['Si guías y protección física para trabajar en áreas seguras se han diseñado e implementado.']
            },
            {
                'subdominio': 'Areas publicas de carga y descarga',
                'preguntas': ['Si las áreas de entrega, carga y otras donde personal no autorizado pueden ingresar a las instalaciones son controladas y centros de procesamiento informáticos están aislados para evitar accesos no autorizados.']
            },
            {
                'subdominio': 'Proteccion de los equipos',
                'preguntas': ['Si los equipos han sido protegidos para reducir los riesgos de amenazas y peligros ambientales como oportunidades de accesos no autorizados.']
            },
            {
                'subdominio': 'Utilitarios de apoyo',
                'preguntas': ['Si los equipos están protegidos de fallas eléctricas como también de otras fallas que pueden ser causadas por fallas en utilitarios de apoyo.', 'Si fuentes de energía permanentes como son múltiples entradas, UPS, generadores, etc. están siendo utilizados.']
            },
            {
                'subdominio': 'Seguridad del cableado',
                'preguntas': ['Si los cables de energía eléctrica y telecomunicaciones que transmiten datos o apoyan los servicios informáticos son protegidos de intercepciones o daños.', 'Si los cables de energía eléctrica y telecomunicaciones que transmiten datos o apoyan los servicios informáticos son protegidos de intercepciones o daños.']
            },
            {
                'subdominio': 'Mantenimiento de equipos',
                'preguntas': ['Si los equipos son mantenidos correctamente para asegurar su disponibilidad e integridad.', ' Si el equipo es mantenido según las especificaciones e intervalos de servicio que recomiendan los proveedores.', 'Si el mantenimiento solo es efectuado por personal autorizado', 'Si registros son mantenidos con todas las posibles fallas o fallas actuales con todas sus medidas preventivas y correctivas.', 'Si controles apropiados han sido implementados cuando se envían equipos fuera de las oficinas.', 'Si el equipo esta cubierto por seguros y si los requisitos del seguro se cumplen.']
            },
            {
                'subdominio': 'Asegurando equipos utilizados fuera de las oficinas',
                'preguntas': ['Si los riesgos fueron evaluados con relación a cualquier uso de equipos fuera de las instalaciones de la organización y controles para mitigar los riesgos han sido implementados.', 'Si el uso de una facilidad de procesamiento de la información localizado fuera de la organización ha sido autorizado por la gerencia.']
            },
            {
                'subdominio': 'Asegurar la re-utilizacion o desecho de equipos',
                'preguntas': ['Si todo equipo que contenga medios de almacenamiento es revisado para asegurarse de que cualquier información sensitiva o software bajo licencia ha sido físicamente destruido o re-grabado en forma segura antes de ser desechado o de su re-utilización.']
            },
            {
                'subdominio': 'Remocion de propiedad',
                'preguntas': ['Si existen controles para que los equipos, información y software no sean llevados fuera de la organización sin previa autorización.']
            },
            {
                'subdominio': 'Procedimientos operativos documentados',
                'preguntas': ['Si el procedimiento operacional esta documentado, mantenido y disponible para todos los usuarios que lo necesiten.', 'Si dichos procedimientos son tratados como un documento formal y por lo tanto cualquier cambio que se necesite hacerle, requiere de la autorización gerencial.']
            },
            {
                'subdominio': 'Control de cambios operacionales',
                'preguntas': ['Si todos los cambios a los centros de procesamiento de la información y los sistemas esta controlado.', 'Si registros de auditoria son mantenidos para reflejar cambios efectuados a los programas productivos.']
            },
            {
                'subdominio': 'Segregacion de funciones',
                'preguntas': ['Si derechos y áreas de responsabilidad son separados con la intención de reducir oportunidades de modificación o mal uso no autorizado de información o servicios.']
            },
            {
                'subdominio': 'Separacion de facilidades de desarrollo y operacionales',
                'preguntas': ['Si las facilidades de desarrollo y pruebas están aisladas de las facilidades operacionales. Ejemplo software de desarrollo solo debe correr en un computador diferente a aquel en que se corre software de producción. Donde sea necesario las redes de desarrollo y producción deben mantenerse separadas.']
            },
            {
                'subdominio': 'Entrega de servicios',
                'preguntas': ['Si se mantienen mediciones para garantizar que los controles de seguridad, definición de servicios y niveles de entrega que se incluyen en el acuerdo de Entrega de Servicios a terceros están implementados, operando y mantenidos por un tercero.']
            },
            {
                'subdominio': 'Monitoreo y revision de servicios de terceros',
                'preguntas': ['Si los servicios, reportes y registros proveídos por terceros son regularmente monitoreados y revisados.', 'Si se efectúan auditorias sobre los servicios de terceros, reportes y registros en forma reiterada.']
            },
            {
                'subdominio': 'Administrando cambios a los servicios de terceros',
                'preguntas': ['Si los cambios para provisionar los servicios, incluyendo mantenimiento y mejoras a políticas, procedimientos y controles de seguridad informática existentes son administrados. Esto toma en consideración la criticidad de los sistemas de negocio, procesos involucrados y la re-evaluación de riesgos.']
            },
            {
                'subdominio': 'Administracion de capacidad',
                'preguntas': ['Si las demanda de capacidad es monitoreada y proyecciones de requisitos futuros son hechos para asegurar un adecuado poder de procesamiento y almacenaje están disponibles.']
            },
            {
                'subdominio': 'Aceptacion de sistemas',
                'preguntas': ['Si criterios para la aceptación de sistemas han sido establecidos para nuevos sistemas informáticos, actualizaciones y nuevas versiones.', ' Si se llevaron a cabo pruebas previas a la aceptación.']
            },
            {
                'subdominio': 'Control contra codigo malicioso',
                'preguntas': ['Si controles para la detección, prevención y control de recuperación para proteger contra código malicioso como también procedimientos de concientizacion del usuario han sido desarrollados e implementados.']
            },
            {
                'subdominio': 'Control contra codigo movil',
                'preguntas': ['Si solo se usa código móvil autorizado. (Código móvil es aquel software que se transfiere de un computador a otro y luego se ejecuta automáticamente. Efectúa un función especifica con con poca o ninguna intervención del usuario. Código móvil esta asociado con un numero de servicios middleware.)', 'Si la configuración asegura que el código móvil autorizado opera según las políticas de seguridad.', 'Si la ejecución de código móvil no autorizado es evitado.']
            },
            {
                'subdominio': 'Respaldo de la informacion',
                'preguntas': ['Si respaldos tanto de informaciones como de software se efectúan con regularidad y se prueban de acuerdo con la política de respaldos acordada.', 'Si toda información y software esencial puede ser recuperada seguido de un desastre o falla de medio.']
            },
            {
                'subdominio': 'Control de la red',
                'preguntas': ['Si la red esta adecuadamente administrada y controlada para protegerla de amenazas y para mantener la seguridad de los sistemas y aplicaciones utilizando la red, incluyendo la información en transito.', 'Si controles fueron implementados para garantizar la seguridad de la información en la red y la protección de servicios conectados de amenazas como ser los accesos no autorizados.']
            },
            {
                'subdominio': 'Seguridad de los servicios de la red',
                'preguntas': ['Si las descripciones de seguridad, niveles de servicio y requisitos administrativos de todos los servicios de la red son identificados e incluidos en cualquier acuerdo de servicios de la red.', 'Si el proveedor de servicios de la red tiene la capacidad de administrar los servicios acordados en una forma segura, definidos y regularmente monitoreados y con el derecho de auditar según lo acordado.']
            },
            {
                'subdominio': 'Administracion de medios removibles',
                'preguntas':  ['Si existen procedimientos para la administración de medios removibles como son las cintas, discos, disquetes, CDs, tarjetas de memoria y reportes.', 'Si todos los procedimientos y niveles de autorización son claramente definidos y documentados.']
            },
            {
                'subdominio': 'Desechar medios',
                'preguntas': ['Si los medios que ya no son requeridos son desechados en forma segura según un procedimiento formal.']
            },
            {
                'subdominio': 'Procedimiento manejo informacion',
                'preguntas': ['Si existe un procedimiento para manejar el almacenaje de la información. Este procedimiento cubre temas como ser la protección de la información de divulgación no autorizada o mal uso.']
            },
            {
                'subdominio': 'Seguridad de documentacion de sistemas',
                'preguntas': ['Si la documentación de sistemas es protegida contra accesos no autorizados.']
            },
            {
                'subdominio': 'Politicas y procedimientos intercambio informacion',
                'preguntas': ['Si existe una política, procedimiento y control de intercambio formal que asegure la protección de la información. El procedimiento y control cubren el uso de facilidades de comunicación electrónica para el intercambio de informaciones.']
            },
            {
                'subdominio': 'Acuerdos de intercambio',
                'preguntas': ['Si se han establecido acuerdos con relación al intercambio de información y software entre la organización y terceros.', 'Si el contenido de seguridad del acuerdo refleja la sensibilidad de la información del negocio involucrada.']
            },
            {
                'subdominio': 'Medios fisicos en transito',
                'preguntas': ['Si los medios conteniendo información es protegida contra accesos no autorizados, mal uso o corrupción durante su transportación fuera de las instalaciones físicas de la organización.']
            },
            {
                'subdominio': 'Mensajeria electronica',
                'preguntas': ['Si la información involucrada en mensajeria electrónica esta bien protegida. (Mensajeria electrónica incluye pero no esta restringida a Correo Electrónico, Transferencia de Datos Electrónicamente (EDI), Mensajeria Instantánea)']
            },
            {
                'subdominio': 'Sistemas informaticos de negocios',
                'preguntas': ['Si políticas y procedimientos han sido desarrollados y reforzados para proteger información asociados con la interconexión de los sistemas informáticos de los negocios.']
            },
            {
                'subdominio': 'Comercio electronico',
                'preguntas': ['Si la información involucrada en el comercio electrónico que se transmite sobre redes publicas esta protegida de actividades fraudulentas, disputas contractuales y cualquier acceso no autorizado o modificaciones.', 'Si controles de seguridad como la aplicación de controles criptográficos se han tomado en consideración.', 'Si acuerdos sobre comercio electrónico entre los socios incluyen un acuerdo documentado el cual compromete a ambas partes a los términos de comercio incluyendo detalles de temas de seguridad.']
            },
            {
                'subdominio': 'Transacciones en linea',
                'preguntas': ['Si informaciones involucradas en transacciones en línea esta protegida para evitar transmisiones incompletas, mal ruteo, alteración no autorizados del mensaje, divulgación no autorizado, duplicación no autorizado del mensaje o respuesta.']
            },
            {
                'subdominio': 'Informacion disponible publicamente',
                'preguntas': ['Si la integridad de información públicamente disponible esta protegida contra modificaciones no autorizadas.']
            },
            {
                'subdominio': 'Log de auditoria',
                'preguntas': ['Si los registros o logs de auditoria registran la actividad de usuarios, excepciones y eventos relacionados con seguridad informática son producidos y mantenidos por un periodo acordado para asistir en futuras investigaciones y monitoreo de control de accesos.']
            },
            {
                'subdominio': 'Monitoreo del uso de sistema',
                'preguntas': ['Si se desarrollaron procedimientos para monitorear el uso de sistemas de las facilidades de procesamientos de informática y se refuerza su cumplimiento.', 'Si los resultados del monitoreo se revisan regularmente.', 'Si el nivel de monitoreo de una facilidad de procesamiento de la información es determinado por una evaluación de riesgo.']
            },
            {
                'subdominio': 'Proteccion de informacion de los registros/logs',
                'preguntas': ['Si las áreas donde se almacenan los registros/logs y las informaciones de los registros/logs están bien protegidas contra manipulación y accesos no autorizados.']
            },
            {
                'subdominio': 'Registros/logs de administradores y operadores',
                'preguntas': ['Si las actividades de los Administradores o Operadores son registradas.', 'Si dichos registros son revisados con regularidad.']
            },
            {
                'subdominio': 'Registros/logs de fallas',
                'preguntas': ['Si fallas son registradas y analizadas y se toman acciones apropiadas.', 'Si el nivel de registro requerido para sistemas individuales es determinado por una evaluación de riesgo tomando en cuenta la degradación en performance.']
            },
            {
                'subdominio': 'Sincronizacion de reloj',
                'preguntas': ['Si el reloj de todos los sistemas de procesamiento de la información dentro de la organización o dominio de seguridad son sincronizados con una fuente acordada.']
            },
            {
                'subdominio': 'Politica de control de acceso',
                'preguntas': ['Si una política de control de accesos ha sido desarrollada y revisada basada en los requisitos del negocio y seguridad.', 'Si ambos controles de acceso tanto físico como lógicos han sido considerados en la política.', 'Si los usuarios y proveedores de servicios se les entrego un claro mensaje sobre los requisitos del negocio a ser cumplidos con relación al control de acceso.']
            },
            {
                'subdominio': 'Registro de usuario',
                'preguntas': ['Si existe un procedimiento formal para el registro o el de-registro de los usuarios para otorgarles acceso a los servicios y sistemas informáticos multi-usuarios.']
            },
            {
                'subdominio': 'Administracion privilegiada',
                'preguntas': ['Si la asignación o uso de cualquier privilegio en los ambientes de los sistemas informáticos esta restringido y controlado. Ej., Privilegios son asignados en base a una necesidad; privilegios son asignados solo después de un proceso formal de autorización.']
            },
            {
                'subdominio': 'Administracion de contraseñas del usuario',
                'preguntas': ['La asignación o re-asignación de contraseñas debe ser controlado por un proceso formal de administración de contraseñas.']
            },
            {
                'subdominio': 'Revision de los derechos de acceso del usuario',
                'preguntas': ['Si existe un proceso para la revisión de los derechos de acceso de los usuarios en forma regular.']
            },
            {
                'subdominio': 'Uso de contraseñas',
                'preguntas': ['Si existen practicas de seguridad que guíen al usuario en seleccionar y mantener contraseñas seguras.']
            },
            {
                'subdominio': 'Equipos de usuario desatendidos',
                'preguntas': ['Si los usuarios y contratistas han sido informados sobre los requisitos de seguridad y los procedimientos para la protección de los equipos desprotegidos. Ejemplo: LogOff cuando la sesión ha terminado o habilitar el auto-logoff, terminar las sesiones cuando termine etc.']
            },
            {
                'subdominio': 'Politica sobre el uso de servicios de la red',
                'preguntas': ['Si a los usuarios se les provee con acceso solo a los servicios que han sido específicamente autorizados a usar.', 'Si existe una política que maneja las temas relacionados con redes y servicios de red.']
            },
            {
                'subdominio': 'Autenticacion del usuario para conexiones externas',
                'preguntas': ['Si existen mecanismos de autenticación adecuados para el control de accesos de usuarios remotos.']
            },
            {
                'subdominio': 'Identificacion de equipos en la red',
                'preguntas': ['Si identificación automática de equipos es considerado como medio para autenticar conexiones de localidades especificas y equipos.']
            },
            {
                'subdominio': 'Diagnostico remoto y configuracion de proteccion de puertos',
                'preguntas': ['Si el acceso lógico y físico a puertos de diagnostico están controlados de forma segura. Ej. Protegidos por un mecanismo de seguridad.']
            },
            {
                'subdominio': 'Segregacion en redes',
                'preguntas': ['Si grupos de servicios informáticos, usuarios y sistemas informáticos están segregados en la red.', 'Si la red (donde socios y/o terceros necesitan accesar los sistemas informáticos) esta segregada utilizando mecanismos de seguridad perimetral como ser un cortafuegos.', 'Si consideraciones se han tomado para segregar redes inalámbricas de redes internas y privadas.']
            },
            {
                'subdominio': 'Protocolo de conexion de redes',
                'preguntas': ['Si existe alguna política de control de acceso el cual establece el control de conexión de redes para redes compartidas; especialmente las que se extienden fuera de las fronteras de la organización.']
            },
            {
                'subdominio': 'Control ruteo de redes',
                'preguntas': ['Si la política de control de accesos establece si controles en el ruteo han de ser implementados para las redes.', 'Si los controles de ruteo están basados en las fuentes positivas y mecanismos de identificación del destinatario. Ejemplo: Network Address Translation (NAT).']
            },
            {
                'subdominio': 'Procedimiento seguro de log-on',
                'preguntas': ['Si el acceso a sistemas operativos es controlado por un procedimiento de log-on seguro.']
            },
            {
                'subdominio': 'Identificacion y autenticacion del usuario',
                'preguntas': ['Si un identificador único es otorgado a cada usuario como son los operadores, administradores de sistemas y todos los demás empleados incluyendo personal técnico.', 'Si se ha escogido una técnica de autenticación aceptable para sustanciar la identidad correspondiente del usuario.']
            },
            {
                'subdominio': 'Sistema de administracion de contraseña',
                'preguntas': ['Si existe un sistema de administración de contraseñas que fuerza varios controles de contraseñas como ser: contraseñas individuales, forzar cambios de las contraseñas, almacenar las contraseñas en forma encriptada, no desplegar las contraseñas en las terminales/pantallas etc.']
            },
            {
                'subdominio': 'Utilizacion de utilitarios de sistemas',
                'preguntas': ['Si los utilitarios de sistemas que vienen con las instalaciones de las computadoras, pero que pueden bypasear controles de los sistemas y aplicaciones son controlados en forma rigurosa.']
            },
            {
                'subdominio': 'Time-out de las sesiones',
                'preguntas': ['Si sesiones inactivas son desactivadas después de un periodo de inactividad definido. (Una forma de inactividad puede ser proveída para algunos sistemas el cual deja en blanco la pantalla y previene el acceso no autorizado pero NO cierra las sesiones de la aplicación o de la Red.']
            },
            {
                'subdominio': 'Limite de tiempo de conexion',
                'preguntas': ['Si existe alguna restricción en el tiempo de conexión para aplicaciones de alto riesgo.']
            },
            {
                'subdominio': 'Restriccion acceso a la informacion',
                'preguntas': ['Si acceso a las funciones de sistemas informáticos y aplicaciones por usuarios y personal de soporte están restringidos de acuerdo con lo definido en la política de control de acceso.']
            },
            {
                'subdominio': 'Aislamiento de sistemas sensitivos',
                'preguntas': ['Si los sistemas sensitivos están proveídos de una ambiente computacional dedicado (aislado) como es el de correr en un computador dedicado, recursos compartidos solo con sistemas de aplicaciones confiables, etc.']
            },
            {
                'subdominio': 'Computacion movil y comunicaciones',
                'preguntas': ['Si existe una Política formal y medidas de seguridad apropiados para proteger contra los riesgos de utilizar computación móvil y facilidades de comunicaciones. Algunos ejemplos de computación móvil y facilidades de comunicación incluyen: notebooks, palms, laptops, smart cards y teléfonos celulares.', 'Si los riesgos tal como es el trabajar en un ambiente no seguro ha sido considerado dentro de la política de computación móvil.']
            },
            {
                'subdominio': 'Teletrabajo',
                'preguntas': ['Si se ha desarrollado e implementado un a Política, plan operacional y procedimiento  para las actividades del teletrabajo.', 'Si la actividad de teletrabajo esta autorizada y controlada por la administración y se asegura de que acuerdos adecuados existen para esta forma de trabajo.']
            },
            {
                'subdominio': 'Requisitos de seguridad, analisis y especificaciones',
                'preguntas': ['Si los requisitos de seguridad para nuevos sistemas informáticos y mejoras a sistemas informáticos existentes especifican los requisitos de controles de seguridad.', 'Si los requisitos de seguridad y controles identificados reflejan los valores del negocio correspondiente a los activos informáticos involucrados y las consecuencias en caso de fallas de Seguridad.', 'Si los requisitos de sistemas para seguridad informática y procesos para la implementación de seguridad son integrados en las etapas iniciales de los proyectos de sistemas informáticos.']
            },
            {
                'subdominio': 'Validaciones de input de datos',
                'preguntas': ['Si el ingreso de datos a las aplicaciones son validados para asegurarse de que son correctos y apropiados.', 'Si los controles tales como: diferentes tipos de datos para validar mensajes de error, procedimientos para responder a errores de validación, definición de responsabilidades de todo el personal involucrados en el proceso de ingreso de datos, etc., son considerados.']
            },
            {
                'subdominio': 'Control de procesos internos',
                'preguntas': ['Si controles de validación son incorporados dentro de la aplicación para detectar cualquier corrupción de información a través de errores de proceso u actos deliberados.', 'Si el diseño e implementación de aplicaciones aseguran que el riesgo de fallas de proceso que conlleven a perdidas de integridad son minimizados.']
            },
            {
                'subdominio': 'Integridad de mensajes',
                'preguntas': ['Si los requisitos para asegurar y proteger la integridad de los mensajes en aplicaciones son identificados y controles apropiados identificados e implementados.', 'Si una evaluación de riesgos de seguridad se llevo a cabo para determinar si la integridad de los mensajes es requerido; y para identificar el método mas apropiado para su implementación']
            },
            {
                'subdominio': 'Validacion de datos de salida',
                'preguntas': ['Si los datos de salida de las aplicaciones es validado para asegurarse que el proceso de datos almacenados es correcto y apropiado según las circunstancias.']
            },
            {
                'subdominio': 'Politica para el uso de controles criptograficos',
                'preguntas': ['Si la organización tiene una Política relacionado con el uso de controles criptográficos para la protección de la información.', 'Si la política ha sido implementada exitosamente.', 'Si la política de criptografía considera la administración hacia el uso de controles criptográficos, resultados de evaluación de riesgos para identificar los niveles de protección necesarios, métodos de administración de llaves y varios estándares para su efectiva implementación.']
            },
            {
                'subdominio': 'Administracion de llaves',
                'preguntas': ['Si existe una administración de llaves que apoye a la organización en el uso de técnicas de criptografía.', 'Si llaves criptográficas son protegidas contra modificaciones, perdidas y destrucción.', 'Si llaves secretas y privadas son protegidas contra divulgación no autorizada.', 'Si los equipos utilizados para generar, almacenar las llaves están físicamente protegidos.', 'Si el sistema de administración de llaves esta basado en un estándar acordado, procedimientos y métodos seguros.']
            },
            {
                'subdominio': 'Control de software operacional',
                'preguntas': ['Si existen controles para la implementación de software en sistemas operativos. Esto es para minimizar el riesgo de corrupción de los sistemas operacionales.']
            },
            {
                'subdominio': 'Proteccion de datos de prueba',
                'preguntas': ['Si los datos de prueba son protegidos y controlados.', 'Si el uso de informaciones personal o cualquier información sensitiva para prueba de bases de datos son enmascarados.']
            },
            {
                'subdominio': 'Control de acceso a librerias de programas fuentes',
                'preguntas': ['Si existen controles estrictos sobre el acceso a la librería de programas fuentes.']
            },
            {
                'subdominio': 'Procedimientos de control de cambios',
                'preguntas': ['Si existen controles estrictos sobre la implementación de cambios a los sistemas informáticos. (Esto es para minimizar la corrupción de los sistemas informáticos).', 'Si este procedimiento considera la necesidad de evaluar riesgos, análisis de impacto sobre los cambios.']
            },
            {
                'subdominio': 'Revision tecnica de aplicaciones despues de cambios a sistemas operacionales',
                'preguntas': ['Si existe un proceso o procedimiento para revisar y probar las aplicaciones criticas del negocio por impactos adversos en operaciones organizacionales o seguridad después de los cambios al sistema operativo. Periódicamente es necesario actualizar los sistemas operativos. Ej. instalar Service Packs, parches, hot fixes, etc.']
            },
            {
                'subdominio': 'Restricciones a cambios a paquetes de software',
                'preguntas': ['Si las modificaciones a paquetes de software son evitados y/o limitados solo a cambios necesarios.', 'Si todos los cambios son estrictamente controlados.']
            },
            {
                'subdominio': 'Divulgacion de informacion',
                'preguntas': ['Si existen los controles para prevenir la divulgación de información.', 'Si controles como es el escaneo de medios saliendo, inspecciones regulares del personal y actividades de sistemas permitidas bajo legislaciones locales, uso de recursos de monitoreo son considerados.']
            },
            {
                'subdominio': 'Desarrollo de sistemas outsourced',
                'preguntas': ['Si el desarrollo de software outsorceado es supervisado y monitoreado por la organización.', 'Si puntos como son: acuerdos de licencia, requisitos contractuales sobre calidad, pruebas antes de instalación para la detección de troyanos etc.; son considerados.']
            },
            {
                'subdominio': 'Control de vulnerabilidades tecnicas',
                'preguntas': ['Si información sobre vulnerabilidades técnicas relacionado con sistemas informáticos utilizados es obtenida en forma regular.', 'Si la exposición de la organización a tales vulnerabilidades han sido evaluadas y medidas apropiadas se han tomado para mitigar los riesgos asociados.']
            },
            {
                'subdominio': 'Reportando eventos de seguridad informaticos',
                'preguntas': ['Si información sobre eventos de seguridad informáticos son reportados a través de canales de administración apropiados tan rápido como es posible.', 'Si un procedimiento formal para reportar eventos de seguridad informática, procedimiento de respuesta y escalacion de Incidentes ha sido desarrollado e implementado.']
            },
            {
                'subdominio': 'Reportando debilidades en la seguridad',
                'preguntas': ['Si existe un procedimiento que asegure que todos los empleados de informática y servicios son requeridos de notificar y reportar cualquier observación o debilidades de seguridad sospechosas en el sistema o servicios.']
            },
            {
                'subdominio': 'Responsabilidades y procedimientos',
                'preguntas': ['Si los procedimientos y responsabilidades administrativas fueron establecidos para asegurar una respuesta rápida, efectiva y ordenada a los incidentes de seguridad informática.', 'Si el monitoreo de alertas y vulnerabilidades de sistemas son utilizados para detectar incidentes de seguridad informática.', 'Si el objetivo de la administración de los incidentes de seguridad informáticos han sido acordados con la gerencia.']
            },
            {
                'subdominio': 'Aprendiendo de incidentes de seguridad informaticos',
                'preguntas': ['Si existe un mecanismo para identificar y cuantificar el tipo, volumen y costos de los incidentes de seguridad informáticos.', 'Si la información obtenida de la evaluación de los incidentes de seguridad informáticos pasados son utilizados para identificar incidentes recurrentes y de alto impacto.']
            },
            {
                'subdominio': 'Colectar evidencia',
                'preguntas': ['Si una acción de seguimiento contra una persona u organización después de un incidente de seguridad informático involucra acciones legales (ya sea civil o criminal).', 'Si evidencia relacionada al incidente es colectada, retenida y presentada para cumplir con las reglas de presentación de evidencia según la jurisdicción.', 'Si procedimientos internos fueron desarrollados y seguidos al colectar y presentar evidencia para el propósito de acciones disciplinarias dentro de la organización.']
            },
            {
                'subdominio': 'Incluyendo seguridad informatica en la continuidad de negocios',
                'preguntas': ['Si existe un proceso administrado que define los requisitos de seguridad informática para el desarrollo y mantenimiento de la continuidad de negocios a través de la organización.', 'Si este proceso contempla los riesgos que la organización esta enfrentando, identificación de activos del negocio críticos, identificación del impacto de incidentes, consideración de la implementación de controles adicionales de prevención y la documentación del plan de continuidad de negocios definiendo los requisitos de seguridad.']
            },
            {
                'subdominio': 'Continuidad de negocios y evaluacion de riesgos',
                'preguntas': ['Si los eventos que causan interrupciones a los procesos del negocio han sido identificados junto con la probabilidad e impacto que tales interrupciones y sus consecuencias por la seguridad informática.']
            },
            {
                'subdominio': 'Desarrollando e implementando planes de continuidad incluyendo seguridad informatica',
                'preguntas': ['Si los planes fueron desarrollados para mantener y restaurar las operaciones del negocio, asegurar la disponibilidad de la información dentro de los niveles requeridos en los tiempos requeridos seguidos a una interrupción o falla a los procesos de negocios.', 'Si el plan considera identificación y acuerdos de responsabilidades, identificación de perdidas aceptables, implementación de procedimientos de recuperación y restauración, documentación de procedimientos y pruebas regulares.']
            },
            {
                'subdominio': 'Arquitectura de planeacion continuidad de negocios',
                'preguntas': ['Si solo existe una arquitectura para el Plan de Continuidad de Negocios.', 'Si esta arquitectura se mantiene para garantizar que todos los planes son consistentes e identifican prioridades para pruebas y mantenimiento.', 'Si el plan de continuidad de negocios define los requisitos sobre seguridad informáticos identificados.']
            },
            {
                'subdominio': 'Pruebas, mantenimiento y re-evaluacion de planes de continuidad de negocios',
                'preguntas': ['Si los Planes de Continuidad de Negocios son probados regularmente  para garantizar que están actualizados y son efectivos.', 'Si las pruebas de los planes de continuidad garantizan que todos los miembros del equipo de recuperación y otros grupos de empleados relevantes están concientes del plan y de sus responsabilidades por la continuidad del negocio y la seguridad informática y conocen su role cuando el plan es activado.']
            },
            {
                'subdominio': 'Identificacion de legislacion aplicable',
                'preguntas': ['Si todos los requisitos relevantes a regulaciones, contratos, etc. y el enfoque organizativo para cumplir los requisitos fueron definidos explícitamente y documentados para cada sistema informático y organización.', 'Si controles específicos y responsabilidades individuales para cumplir con los requisitos fueron definidos y documentados.']
            },
            {
                'subdominio': 'Derechos de propiedad intelectual',
                'preguntas': ['Si existen procedimientos que garanticen el cumplimiento con requisitos legislativos, regulaciones y contratos en el uso de material en el cual pueden existir derechos de propiedad intelectual y en el uso de productos de software propietarios.', 'Si los procedimientos están bien implementados.', 'Si controles como son: políticas de cumplimiento sobre los derechos de publicación de propiedad intelectual, procedimientos para la adquisición de software, políticas de concientizacion, mantener prueba de propiedad, cumpliendo con los términos y condiciones han sido considerado.']
            },
            {
                'subdominio': 'Proteccion de registros organizacionales',
                'preguntas': ['Si registros importantes de la organización son protegidos de perdidas, destrucción y falsificación de acuerdo con regulaciones, contratos y requisitos de negocios.', 'Si se ha considerado la posibilidad del deterioro de los medios de para el almacenaje de los registros.', 'Si los sistemas de almacenamiento de datos fueron escogidos para que datos requeridos puedan ser recuperados o restaurados en un tiempo y formato aceptable, dependiendo en los requisitos a cumplir.']
            },
            {
                'subdominio': 'Proteccion de datos y privacidad de datos personales',
                'preguntas': ['Si la protección y privacidad de los datos es asegurada según legislación, regulación relevantes y si es aplicable según cláusulas contractuales.']
            },
            {
                'subdominio': 'Prevencion del mal uso de las facilidades de procesos informaticos',
                'preguntas': ['Si el uso de las facilidades de procesos informáticos para efectos personales o no autorizados sin el consentimiento de la gerencia es tratado como uso inapropiado de las facilidades.', 'Si un mensaje de advertencia al momento de log-on es presentado en la pantalla previo a su logon. El usuario tiene que reconocer la advertencia y reaccionar adecuadamente al mensaje en la pantalla para continuar con su proceso de logon.', 'Si se obtiene asesoria legal antes de implementar cualquier procedimiento de monitoreo.']
            },
            {
                'subdominio': 'Regulacion de controles criptografico',
                'preguntas': ['Si los controles criptográficos son utilizados en cumplimiento con acuerdo, leyes y regulaciones relevantes.']
            },
            {
                'subdominio': 'Cumplimiento con politicas y estandares de seguridad',
                'preguntas': ['Si los gerentes aseguran que todos los procedimientos de seguridad dentro de sus áreas de responsabilidad son efectuados correctamente para lograr cumplimiento con las políticas y estándares de seguridad.', 'Los Gerentes revisan periódicamente el cumplimiento de las facilidades de procesamiento informáticos dentro de sus área de responsabilidad para el cumplimiento con procedimientos y políticas de seguridad apropiados.']
            },
            {
                'subdominio': 'Revision del cumplimiento tecnico',
                'preguntas': ['Si los sistemas informáticos son regularmente revisados con relación al cumplimiento con la implementación de estándares de seguridad.', 'Si la revisión del cumplimiento técnico es efectuado por o bajo la supervisión de personal competente y autorizado.']
            },
            {
                'subdominio': 'Controles de auditoria de sistemas informaticos',
                'preguntas': ['Si los requisitos de auditoria y actividades que involucran revisiones de los sistemas operacionales deben ser planeadas cuidadosamente y acordadas para minimizar los riesgos o interrupciones a los procesos de negocio.', 'Si los requisitos de auditoria y alcance han sido acordados con la gerencia apropiada.']
            },
            {
                'subdominio': 'Proteccion de las herramientas de auditorias de sistemas informaticos',
                'preguntas': ['Si acceso a las herramientas de auditoria de sistemas como ser software o archivos de datos son protegidos para prevenir posible mal uso o compromisos.', 'Si las herramientas de auditoria de sistemas informáticos son separados de los sistemas de desarrollo y operacionales a menos que se les haya dado un nivel apropiado de protección adicional.']
            }

        ]

        subdominios = Subdominio.objects.filter(dominio__empresa=empresa.id)
        aux_encontrado = False
        for subdom in subdominios:
            for p in preguntas:
                if p['subdominio'] == subdom.nombre:
                    aux_encontrado = True
                    for preg in p['preguntas']:
                        pregunta_nuevo = Pregunta(titulo=preg, subdominio=subdom, usuario=nuevo_perfil)
                        pregunta_nuevo.save()
                if aux_encontrado == True:
                    aux_encontrado = False
                    break

        return HttpResponseRedirect(reverse('usuario_list'))
    return render(request, template_name, context)


def usuario_delete(request):
    context = {}
    template_name = 'encuesta/administrador/usuarios/usuario_delete.html'
    empresas = list(Empresa.objects.exclude(id=request.user.usuario.empresa.id).values('id', 'nombre'))
    context['empresas'] = empresas
    if request.method == "GET":
        form = UsuarioForm()
        context['form'] = form
    elif request.method == "POST" and request.is_ajax():
        usuario = Usuario.objects.get(id=request.POST.get('usuario'))
        usuario.user.delete()
        data = {
            'ok': True,
            'mensaje': 'Usuario eliminado correctamente'
        }
        return JsonResponse(data)

    return render (request, template_name, context)


def empresa_add(request):
    context = {}
    data = {}
    template_name = "encuesta/administrador/usuarios/usuario_add.html"
    
    if request.method == "POST" and request.is_ajax():
        nombre_empresa = request.POST.get('nombre_empresa')
        if len(nombre_empresa) == 0:
            data['msg_error'] = 'Escriba un nombre de empresa'
            data['ok'] = False
        elif not re.match(r'^[a-z-A-Z][a-z-A-Z\s]*$', nombre_empresa):
            data['msg_error'] = 'Solo se aceptan letras para el nombre de la empresa'
            data['ok'] = False
        else:
            resultado = Empresa.objects.filter(nombre__iexact=nombre_empresa).exists()
            if resultado:
                data['msg_error'] = 'Esta nombre de empresa ya existe'
                data['ok'] = False
            else:
                nueva_empresa = Empresa(nombre=nombre_empresa)
                nueva_empresa.save()
                dominios = [
                    {
                        'nombre': 'Politica de seguridad',
                        'subdominios': ['Documento politica seguridad informatica', 'Revision de politica seguridad informatica']
                    },
                    {
                        'nombre': 'Organizacion de la seguridad informatica',
                        'subdominios': ['Compromiso gerencial a la seguridad informatica', 'Coordinacion seguridad informatica', 'Distribucion responsabilidades seguridad informatica', 'Proceso autorizacion para facilidades de procesos informaticos', 'Acuerdos de confidencialidad', 'Contacto con autoridades', 'Contacto con grupos de interes especial', 'Revision independiente de la seguridad informatica', 'Identificacion de riesgos por accesos de externos', 'Manejando la seguridad al tratar con clientes', 'Manejando la seguridad en acuerdos con terceros']
                    },
                    {
                        'nombre': 'Administracion activos',
                        'subdominios': ['Inventario de activos', 'Dueños de activos', 'Uso aceptable de activos', 'Guia de clasificacion', 'Etiquetado y manejo de la informacion']
                    },
                    {
                        'nombre': 'Seguridad recursos humanos',
                        'subdominios': ['Roles y responsabilidades', 'Revision antecedentes', 'Terminos y condiciones de empleo', 'Terminos y condiciones de trabajo', 'Responsabilidades administrativas', 'Concientizacion, educacion y entrenamiento sobre seguridad informatica', 'Proceso disciplinario', 'Responsabilidades de termino', 'Devolucion de activos', 'Eliminacion de derechos de acceso']
                    },
                    {
                        'nombre': 'Seguridad fisica y ambiental',
                        'subdominios': ['Perimetro seguridad fisica', 'Controles de ingreso fisico', 'Asegurar oficinas, cuartos y facilidades', 'Protegiendo contra amenazas externas y ambientales', 'Trabajando en areas seguras', 'Areas publicas de carga y descarga', 'Proteccion de los equipos', 'Utilitarios de apoyo', 'Seguridad del cableado', 'Mantenimiento de equipos', 'Asegurando equipos utilizados fuera de las oficinas', 'Asegurar la re-utilizacion o desecho de equipos', 'Remocion de propiedad']
                    },
                    {
                        'nombre': 'Administracion, comunicacion y operaciones',
                        'subdominios': ['Procedimientos operativos documentados', 'Control de cambios operacionales', 'Segregacion de funciones', 'Separacion de facilidades de desarrollo y operacionales', 'Entrega de servicios', 'Monitoreo y revision de servicios de terceros', 'Administrando cambios a los servicios de terceros', 'Administracion de capacidad', 'Aceptacion de sistemas', 'Control contra codigo malicioso', 'Control contra codigo movil', 'Respaldo de la informacion', 'Control de la red', 'Seguridad de los servicios de la red', 'Administracion de medios removibles', 'Desechar medios', 'Procedimiento manejo informacion', 'Seguridad de documentacion de sistemas', 'Politicas y procedimientos intercambio informacion', 'Acuerdos de intercambio', 'Medios fisicos en transito', 'Mensajeria electronica', 'Sistemas informaticos de negocios', 'Comercio electronico', 'Transacciones en linea', 'Informacion disponible publicamente', 'Log de auditoria', 'Monitoreo del uso de sistema', 'Proteccion de informacion de los registros/logs', 'Registros/logs de administradores y operadores', 'Registros/logs de fallas', 'Sincronizacion de reloj']
                    },
                    {
                        'nombre': 'Control de accesos',
                        'subdominios': ['Politica de control de acceso', 'Registro de usuario', 'Administracion privilegiada', 'Administracion de contraseñas del usuario', 'Revision de los derechos de acceso del usuario', 'Uso de contraseñas', 'Equipos de usuario desatendidos', 'Politica sobre el uso de servicios de la red', 'Autenticacion del usuario para conexiones externas', 'Identificacion de equipos en la red', 'Diagnostico remoto y configuracion de proteccion de puertos', 'Segregacion en redes', 'Protocolo de conexion de redes', 'Control ruteo de redes', 'Procedimiento seguro de log-on', 'Identificacion y autenticacion del usuario', 'Sistema de administracion de contraseña', 'Utilizacion de utilitarios de sistemas', 'Time-out de las sesiones', 'Limite de tiempo de conexion', 'Restriccion acceso a la informacion', 'Aislamiento de sistemas sensitivos', 'Computacion movil y comunicaciones', 'Teletrabajo']
                    },
                    {
                        'nombre': 'Adquision, desarrollo y mantemiento de sistemas informaticos',
                        'subdominios': ['Requisitos de seguridad, analisis y especificaciones', 'Validaciones de input de datos', 'Control de procesos internos', 'Integridad de mensajes', 'Validacion de datos de salida', 'Politica para el uso de controles criptograficos', 'Administracion de llaves', 'Control de software operacional', 'Proteccion de datos de prueba', 'Control de acceso a librerias de programas fuentes', 'Procedimientos de control de cambios', 'Revision tecnica de aplicaciones despues de cambios a sistemas operacionales', 'Restricciones a cambios a paquetes de software', 'Divulgacion de informacion', 'Desarrollo de sistemas outsourced', 'Control de vulnerabilidades tecnicas']
                    },
                    {
                        'nombre': 'Administracion de incidentes de seguridad informatica',
                        'subdominios': ['Reportando eventos de seguridad informaticos', 'Reportando debilidades en la seguridad', 'Responsabilidades y procedimientos', 'Aprendiendo de incidentes de seguridad informaticos', 'Colectar evidencia']
                    },
                    {
                        'nombre': 'Administracion continuidad de negocios',
                        'subdominios': ['Incluyendo seguridad informatica en la continuidad de negocios', 'Continuidad de negocios y evaluacion de riesgos', 'Desarrollando e implementando planes de continuidad incluyendo seguridad informatica', 'Arquitectura de planeacion continuidad de negocios', 'Pruebas, mantenimiento y re-evaluacion de planes de continuidad de negocios']
                    },
                    {
                        'nombre': 'Cumplimiento',
                        'subdominios': ['Identificacion de legislacion aplicable', 'Derechos de propiedad intelectual', 'Proteccion de registros organizacionales', 'Proteccion de datos y privacidad de datos personales', 'Prevencion del mal uso de las facilidades de procesos informaticos', 'Regulacion de controles criptografico', 'Cumplimiento con politicas y estandares de seguridad', 'Revision del cumplimiento tecnico', 'Controles de auditoria de sistemas informaticos', 'Proteccion de las herramientas de auditorias de sistemas informaticos']
                    }
                ]
                
                for dom in dominios:
                    dom_nuevo = Dominio(nombre=dom['nombre'], empresa=nueva_empresa)
                    dom_nuevo.save()
                    for subdom in dom['subdominios']:
                        subdom_nuevo = Subdominio(nombre=subdom, dominio=dom_nuevo)
                        subdom_nuevo.save()
                
                data['ok'] = True
                data['msg_success'] = 'Se creo correctamente la empresa'
        return JsonResponse(data)


def admin_pregunta_add(request):
    context = {}
    template_name = 'encuesta/administrador/preguntas/add_pregunta.html'

    empresas = list(Empresa.objects.exclude(id=request.user.usuario.empresa.id).values('id', 'nombre'))
    context['empresas'] = empresas
    if request.is_ajax():
        data = {}
        dom_request = request.GET['dominio']
        print(dom_request)
        if dom_request == '---':
            data['subdominios'] = []
            return JsonResponse(data)
        dominios = [
            {
                'nombre': 'Politica de seguridad',
                'subdominios': ['Documento politica seguridad informatica', 'Revision de politica seguridad informatica']
            },
            {
                'nombre': 'Organizacion de la seguridad informatica',
                'subdominios': ['Compromiso gerencial a la seguridad informatica', 'Coordinacion seguridad informatica', 'Distribucion responsabilidades seguridad informatica', 'Proceso autorizacion para facilidades de procesos informaticos', 'Acuerdos de confidencialidad', 'Contacto con autoridades', 'Contacto con grupos de interes especial', 'Revision independiente de la seguridad informatica', 'Identificacion de riesgos por accesos de externos', 'Manejando la seguridad al tratar con clientes', 'Manejando la seguridad en acuerdos con terceros']
            },
            {
                'nombre': 'Administracion activos',
                'subdominios': ['Inventario de activos', 'Dueños de activos', 'Uso aceptable de activos', 'Guia de clasificacion', 'Etiquetado y manejo de la informacion']
            },
            {
                'nombre': 'Seguridad recursos humanos',
                'subdominios': ['Roles y responsabilidades', 'Revision antecedentes', 'Terminos y condiciones de empleo', 'Terminos y condiciones de trabajo', 'Responsabilidades administrativas', 'Concientizacion, educacion y entrenamiento sobre seguridad informatica', 'Proceso disciplinario', 'Responsabilidades de termino', 'Devolucion de activos', 'Eliminacion de derechos de acceso']
            },
            {
                'nombre': 'Seguridad fisica y ambiental',
                'subdominios': ['Perimetro seguridad fisica', 'Controles de ingreso fisico', 'Asegurar oficinas, cuartos y facilidades', 'Protegiendo contra amenazas externas y ambientales', 'Trabajando en areas seguras', 'Areas publicas de carga y descarga', 'Proteccion de los equipos', 'Utilitarios de apoyo', 'Seguridad del cableado', 'Mantenimiento de equipos', 'Asegurando equipos utilizados fuera de las oficinas', 'Asegurar la re-utilizacion o desecho de equipos', 'Remocion de propiedad']
            },
            {
                'nombre': 'Administracion, comunicacion y operaciones',
                'subdominios': ['Procedimientos operativos documentados', 'Control de cambios operacionales', 'Segregacion de funciones', 'Separacion de facilidades de desarrollo y operacionales', 'Entrega de servicios', 'Monitoreo y revision de servicios de terceros', 'Administrando cambios a los servicios de terceros', 'Administracion de capacidad', 'Aceptacion de sistemas', 'Control contra codigo malicioso', 'Control contra codigo movil', 'Respaldo de la informacion', 'Control de la red', 'Seguridad de los servicios de la red', 'Administracion de medios removibles', 'Desechar medios', 'Procedimiento manejo informacion', 'Seguridad de documentacion de sistemas', 'Politicas y procedimientos intercambio informacion', 'Acuerdos de intercambio', 'Medios fisicos en transito', 'Mensajeria electronica', 'Sistemas informaticos de negocios', 'Comercio electronico', 'Transacciones en linea', 'Informacion disponible publicamente', 'Log de auditoria', 'Monitoreo del uso de sistema', 'Proteccion de informacion de los registros/logs', 'Registros/logs de administradores y operadores', 'Registros/logs de fallas', 'Sincronizacion de reloj']
            },
            {
                'nombre': 'Control de accesos',
                'subdominios': ['Politica de control de acceso', 'Registro de usuario', 'Administracion privilegiada', 'Administracion de contraseñas del usuario', 'Revision de los derechos de acceso del usuario', 'Uso de contraseñas', 'Equipos de usuario desatendidos', 'Politica sobre el uso de servicios de la red', 'Autenticacion del usuario para conexiones externas', 'Identificacion de equipos en la red', 'Diagnostico remoto y configuracion de proteccion de puertos', 'Segregacion en redes', 'Protocolo de conexion de redes', 'Control ruteo de redes', 'Procedimiento seguro de log-on', 'Identificacion y autenticacion del usuario', 'Sistema de administracion de contraseña', 'Utilizacion de utilitarios de sistemas', 'Time-out de las sesiones', 'Limite de tiempo de conexion', 'Restriccion acceso a la informacion', 'Aislamiento de sistemas sensitivos', 'Computacion movil y comunicaciones', 'Teletrabajo']
            },
            {
                'nombre': 'Adquision, desarrollo y mantemiento de sistemas informaticos',
                'subdominios': ['Requisitos de seguridad, analisis y especificaciones', 'Validaciones de input de datos', 'Control de procesos internos', 'Integridad de mensajes', 'Validacion de datos de salida', 'Politica para el uso de controles criptograficos', 'Administracion de llaves', 'Control de software operacional', 'Proteccion de datos de prueba', 'Control de acceso a librerias de programas fuentes', 'Procedimientos de control de cambios', 'Revision tecnica de aplicaciones despues de cambios a sistemas operacionales', 'Restricciones a cambios a paquetes de software', 'Divulgacion de informacion', 'Desarrollo de sistemas outsourced', 'Control de vulnerabilidades tecnicas']
            },
            {
                'nombre': 'Administracion de incidentes de seguridad informatica',
                'subdominios': ['Reportando eventos de seguridad informaticos', 'Reportando debilidades en la seguridad', 'Responsabilidades y procedimientos', 'Aprendiendo de incidentes de seguridad informaticos', 'Colectar evidencia']
            },
            {
                'nombre': 'Administracion continuidad de negocios',
                'subdominios': ['Incluyendo seguridad informatica en la continuidad de negocios', 'Continuidad de negocios y evaluacion de riesgos', 'Desarrollando e implementando planes de continuidad incluyendo seguridad informatica', 'Arquitectura de planeacion continuidad de negocios', 'Pruebas, mantenimiento y re-evaluacion de planes de continuidad de negocios']
            },
            {
                'nombre': 'Cumplimiento',
                'subdominios': ['Identificacion de legislacion aplicable', 'Derechos de propiedad intelectual', 'Proteccion de registros organizacionales', 'Proteccion de datos y privacidad de datos personales', 'Prevencion del mal uso de las facilidades de procesos informaticos', 'Regulacion de controles criptografico', 'Cumplimiento con politicas y estandares de seguridad', 'Revision del cumplimiento tecnico', 'Controles de auditoria de sistemas informaticos', 'Proteccion de las herramientas de auditorias de sistemas informaticos']
            }
        ]

        for dom in dominios:
            if dom['nombre'] == dom_request:
                data['subdominios'] = dom['subdominios']
                data['ok'] = True
                break

        return JsonResponse(data)
    elif request.method == "POST":
        print(request.POST)
        subdominio_nombre = request.POST.get('subdominioSelect')
        dominio_nombre = request.POST.get('dominioSelect')
        pregunta_titulo = request.POST.get('pregunta')

        subdominios = Subdominio.objects.filter(nombre=subdominio_nombre, dominio__nombre=dominio_nombre)
        print(subdominios)

        for subdom in subdominios:
            usuarios = Usuario.objects.filter(empresa=subdom.dominio.empresa)
            for usuario in usuarios:
                pregunta_nueva = Pregunta(titulo=pregunta_titulo, subdominio=subdom, usuario=usuario)
                pregunta_nueva.save()
        
        messages.success(request, 'Pregunta creada correctamente')
        return redirect('index')

    return render(request, template_name, context)

