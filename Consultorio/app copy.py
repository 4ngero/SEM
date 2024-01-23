from flask import Flask, render_template, request, redirect, url_for,flash,session, jsonify,Response
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user,logout_user,login_required, UserMixin
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Flowable, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from xhtml2pdf import pisa
from datetime import datetime



app = Flask(__name__)
app.secret_key='mysecretapp'
try: 
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] ='root'
    app.config['MYSQL_PASSWORD']=''
    app.config['MYSQL_DB']='bdconsultorio'
    app.secret_key = 'mysecretkey'
    mysql = MySQL(app)
    print("Conexion exitosa")
except Exception as ex:
    print(ex)

global_idpaciente = None
#Ruta principal ------------------------------
@app.route('/')
def login():
    return render_template('login.html') 

# Creamos la clase pare guardar el Usuario para las interface
class User(UserMixin):
    def __init__(self, id, Vrfc ,Vpass):
        self.id = id
        self.Vrfc = Vrfc
        self.Vpass = Vpass
    
    def get_id(self):
        return str(self.id)
#Obliga a iniciar sesion 
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message= 'Acceso denegado... Inicia Sesión para acceder'

#Guardamos la sesion 
@login_manager.user_loader
def load_user(id):
    print('Este es mi id:' + id)
    CS = mysql.connection.cursor()
    CS.execute('Select id, rfc, contraseña from medicos where id =%s', (id,))
    usuario = CS.fetchone()
    if usuario:
        print("Método: load_user(id), el usuario si coincide.")
        return User(id=usuario[0], Vrfc=[1], Vpass=[6])
    return None


#Metodo iniciar sesion --------------------------------------------------
@app.route('/iniciosesion', methods=['POST'])
def iniciosesion():
    if request.method == 'POST':
        rfc = request.form['txtusuario']
        contraseña = request.form['txtpass']
        
        if rfc == "" or contraseña == "":
            flash('No se puede entrar con campos vacios')
            return render_template('login.html')
        else:
            CS = mysql.connection.cursor()
            # Consulta para verificar las credenciales del usuario
            consulta = "SELECT * FROM medicos WHERE rfc = %s"
            CS.execute(consulta,(rfc,))
            usuario = CS.fetchone()
            mysql.connection.commit()
            # Iniciar sesión exitosa
            if usuario:
                row = usuario[6]
                rol = usuario[7]
                if check_password_hash(row,contraseña):
                    CS = mysql.connection.cursor()
                    # Consulta para verificar las credenciales del usuario
                    consulta = "SELECT * FROM medicos WHERE rfc = %s"
                    CS.execute(consulta,(rfc,))
                    usuario = CS.fetchone()
                    mysql.connection.commit()
                    session['rol'] = rol  # Almacena el rol en la sesión
                    session['cedula_medico'] = usuario[4]
                    session['rfc_medico'] = usuario[1]
                    user = User(id=usuario[0], Vrfc=[1], Vpass=[6])
                    print(user)
                    login_user(user)
                    flash('Ingresar medico')
                    return redirect(url_for('inicio'))
                else:
                    flash('Contraseña incorrecta, favor de reintentar...')
                    return render_template('login.html')
            else:
                flash('RFC ingresado no existe, favor de reintentar...')
                return render_template('login.html')
                
# Cerrar sesion incluyendo el usuario con la sesion guardada------
@app.route('/Cerrarsesion')
def cerrarsesion():
    logout_user()
    flash("Sesion cerrada correctamente, ¡Hasta luego!")
    return redirect(url_for('login'))

@app.route('/ConsultorioMedico')
@login_required
def inicio():
    return render_template('inicio.html')

# ---------------------------  Opciones administrador ---------------------------------------
@app.route('/RegistroMedico')
@login_required
def interfazM():
    if session:
        rol = session.get('rol')  # Obtenemos el rol de la sesión
        if rol == 1:
            return render_template('formmedico.html')
        else:
            flash('No es administrador')
            return render_template('inicio.html')
    else:
        return render_template('login.html')

@app.route('/RegistrarMedico', methods=['POST'])
@login_required
def registrarM():
    if request.method == 'POST':
        Vnombre= request.form['txtNombre']
        Vapellido= request.form['txtApellido']
        Vcedula= request.form['txtcedula']
        Vrfc= request.form['txtrfc']
        Vcorreo= request.form['txtcorreo']
        Vcontrasena= request.form['txtpass']
        Vpass= request.form['txtpassw']
        Vrol= request.form['txtrol']
        #print(Vnombre,Vapellido,Vcedula,Vrfc,Vcontrasena,Vpass,Vrol)

        if Vnombre == "" or Vapellido == "" or Vcedula == "" or Vrfc == "" or Vapellido == "" or Vcontrasena == "" or Vpass == "" or Vrol == "Elegir...":
            flash('No se pueden guardar campos vacios')
            return render_template('formmedico.html')
        else:
            if Vcontrasena == Vpass:
                Encrippass = generate_password_hash(Vcontrasena, 'pbkdf2:sha256')
                print(check_password_hash(Encrippass,Vcontrasena))
                #Conectar y ejecutar el insert
                CS = mysql.connection.cursor()
                CS.execute('insert into medicos(rfc,nombre,apellidos,cedula,correo,contraseña,rol) values (%s,%s,%s,%s,%s,%s,%s)',(Vrfc,Vnombre,Vapellido,Vcedula,Vcorreo,Encrippass,Vrol))
                mysql.connection.commit()
                flash('El médico se guardo correctamente')
                return render_template('formmedico.html')
            else:
                flash('Las contraseñas no coinciden, favor de reintentar')
                return render_template('formmedico.html')


@app.route('/ConsultarMedico')
@login_required
def consulta():
    rol = session.get('rol')  # Obtenemos el rol de la sesión
    if rol == 1:
        CC= mysql.connection.cursor()
        CC.execute('select * from medicos')
        medicos= CC.fetchall()
        return render_template('cmedico.html', listamedico = medicos)
    else:
        flash('No es administrador')
        return render_template('inicio.html')

#Consultamos por nombre-------------------------------------------------
@app.route('/Consultanombre', methods=['POST'])
@login_required
def consultanombre():
    Varbuscar= request.form['txtbuscar']
    CC= mysql.connection.cursor()
    CC.execute('select * from medicos where nombre LIKE %s', (f'%{Varbuscar}%',))
    medicos= CC.fetchall()
    return render_template('cmedico.html', listamedico = medicos)

# Ruta editar médico -------------------------------------------------
@app.route('/editar/<id>')
@login_required
def editarmedico(id):
    CSid = mysql.connection.cursor()
    CSid.execute('select * from medicos where id = %s', (id,))
    Consid = CSid.fetchone()
    return render_template('amedico.html', med= Consid) 

@app.route('/actualizar/<id>', methods=['POST'])
@login_required
def actualizar(id):
    if request.method == 'POST':
        Vnombre= request.form['txtNombre']
        Vapellido= request.form['txtApellido']
        Vcedula= request.form['txtcedula']
        Vrfc= request.form['txtrfc']
        Vcorreo= request.form['txtcorreo']
        Vcontrasena= request.form['txtpass']
        Vpass= request.form['txtpassw']
        Vrol= request.form['txtrol']
        
        if Vnombre == "" or Vapellido == "" or Vcedula == "" or Vrfc == "" or Vcontrasena == "" or Vpass == "" or Vrol == "Elegir...":
            flash('No se pueden actualizar campos vacios')
            #Regresamos a la interfaz y con ella los datos ya insertados
            CSid = mysql.connection.cursor()
            CSid.execute('select * from medicos where id = %s', (id,))
            Consid = CSid.fetchone()
            return render_template('amedico.html', med= Consid) 
        else:
            CSid = mysql.connection.cursor()
            CSid.execute('select * from medicos where id = %s', (id,))
            Consid = CSid.fetchone()
            passwo = Consid[6]
            #Comparamos la contraseña con la BD para ver si son iguales
            if passwo==Vcontrasena:
                CSedit= mysql.connection.cursor()
                CSedit.execute('update medicos set rfc= %s, nombre= %s, apellidos= %s, cedula= %s, correo= %s, contraseña= %s, rol= %s where id= %s', (Vrfc, Vnombre, Vapellido, Vcedula, Vcorreo, Vcontrasena, Vrol, id,))
                mysql.connection.commit()
                
                CC = mysql.connection.cursor()
                CC.execute('select * from medicos')
                medicos = CC.fetchall()
                flash('El Médico se actualizó correctamente')
                return render_template('cmedico.html', listamedico=medicos)
            else:
                #Si el usuario introduce nuevas contraseñas, se comparan 
                if Vcontrasena == Vpass:
                    Encrippass = generate_password_hash(Vcontrasena, 'pbkdf2:sha256')
                    print(check_password_hash(Encrippass,Vcontrasena))
            
                    CSedit= mysql.connection.cursor()
                    CSedit.execute('update medicos set rfc= %s, nombre= %s, apellidos= %s, cedula= %s, correo= %s, contraseña= %s, rol= %s where id= %s', (Vrfc, Vnombre, Vapellido, Vcedula, Vcorreo, Encrippass, Vrol, id,))
                    mysql.connection.commit()
                    
                    CC = mysql.connection.cursor()
                    CC.execute('select * from medicos')
                    medicos = CC.fetchall()
                    flash('El Médico se actualizó correctamente')
                    return render_template('cmedico.html', listamedico=medicos)
                else:
                    flash('Las contraseñas no coinciden')
                    CSid = mysql.connection.cursor()
                    CSid.execute('select * from medicos where id = %s', (id,))
                    Consid = CSid.fetchone()
                    return render_template('amedico.html', med= Consid)
        
# Eliminar médico -------------------------------------------------------
@app.route('/borrar/<id>', methods=['POST'])
@login_required
def eliminar(id):
    if request.method == 'POST':
        CSeli = mysql.connection.cursor()
        CSeli.execute('delete from medicos where id= %s',(id,))
        mysql.connection.commit()
        return jsonify({'message': 'success'})
    return jsonify({'message': 'error'})

#---------------------------------------------------------------------------------------------------------

#------------------------------------- Pacientes --------------------------------------------------------
@app.route('/Expedientepaciente')
@login_required
def introexpac():
    cedula_medico = session.get('cedula_medico')
    return render_template('expaciente.html', cedula_medico = cedula_medico)

global_edad = None 
#---------------- Registrar pacientes ------------------------------------------------------------------
@app.route('/Registropaciente', methods=['POST'])
@login_required
def Registropaciente():
    if request.method == 'POST':
        cedula_medico = session.get('cedula_medico')
        Vcedula = cedula_medico
        Vnombre = request.form['txtNombre']
        Vapellido = request.form['txtApellido']
        Vnacimiento = request.form['txtnacimiento']
        Venfermedades = request.form['txtenfermedades'] if 'txtenfermedades' in request.form else ""
        Valergias = request.form['txtalergias'] if 'txtalergias' in request.form else ""
        Vantecedentes = request.form['txtantecedentes'] if 'txtantecedentes' in request.form else ""
        #print(Vcedula, Vnombre, Vapellido, Vnacimiento, Venfermedades, Valergias, Vantecedentes)
        if Vcedula == "" or Vnombre == "" or Vapellido =="" or Vnacimiento == "" or Venfermedades == "" or Valergias == "" or Vantecedentes == "":
            flash('No se pueden guardar campos vacíos')
            return render_template('expaciente.html') 
        else:      
            CSid = mysql.connection.cursor()
            CSid.execute('SELECT cedula FROM medicos WHERE cedula=%s', (Vcedula,))
            Consid = CSid.fetchone()
            if Consid is None:
                flash('La cédula ingresada no existe en la base de datos')
                return render_template('expaciente.html')
            else:
                if Venfermedades == 'Otra':
                    Venfermedadesotro = request.form['txtenfermedades_otro']
                    if Venfermedadesotro == "":
                        flash('No se pueden guardar campos vacíos')
                        return render_template('expaciente.html')
                    else:
                        Venfermedades = Venfermedadesotro

                if Valergias == 'Otro':
                    Valergiasotro = request.form['txtalergias_otro']
                    if Valergiasotro == "":
                        flash('No se pueden guardar campos vacíos')
                        return render_template('expaciente.html')
                    else:
                        Valergias = Valergiasotro

                if Vantecedentes == 'Otro':
                    Vantecedentesotro = request.form['txtantecedentes_otro']
                    if Vantecedentesotro == "":
                        flash('No se pueden guardar campos vacíos')
                        return render_template('expaciente.html')
                    else:
                        Vantecedentes = Vantecedentesotro
                CS = mysql.connection.cursor()
                CS.execute('insert into pacientes(cedulamedico,nombre,apellidos,fechanacimiento,enfermedades,alergias,antecedentes) values (%s,%s,%s,%s,%s,%s,%s)', (Vcedula, Vnombre, Vapellido, Vnacimiento, Venfermedades, Valergias, Vantecedentes))
                mysql.connection.commit()
                flash('El paciente se guardó correctamente')
                cedula_medico = session.get('cedula_medico')
                return render_template('expaciente.html', cedula_medico = cedula_medico)
            
# Ruta Exploracion y diagnostigo ---------------------------------------------------
@app.route('/Exploracionpacie')
@login_required
def exploracionpacientes():
    cedula_medico = session.get('cedula_medico')
    CS = mysql.connection.cursor()
    CS.execute('select * from pacientes where cedulamedico = %s', (cedula_medico,))
    Consultas = CS.fetchall()
    return render_template('cesxploracion.html', listapacientes = Consultas)

@app.route('/Exploracionpac', methods=['POST'])
@login_required
def exploracionpacie():
    Varbuscar= request.form['txtbuscar']
    CC= mysql.connection.cursor()
    CC.execute('select * from pacientes where nombre LIKE %s', (f'%{Varbuscar}%',))
    consultapac= CC.fetchall()
    return render_template('cesxploracion.html', listapacientes = consultapac)


@app.route('/Exploracion/<id>')
def exploracion(id):
    global global_idpaciente
    fechahoy = datetime.today().strftime('%Y-%m-%d')
    cedula_medico = session.get('cedula_medico')
    CSid = mysql.connection.cursor()
    CSid.execute('select * from pacientes where id = %s', (id,))
    global_idpaciente = id
    Consid = CSid.fetchone()
    return render_template('exploracion.html', pac = Consid, cedula=cedula_medico, fecha=fechahoy) 


@app.route('/registrar_exploracion', methods=['POST'])
def registrar_exploracion():
    if request.method == 'POST':
        Vcedula = session.get('cedula_medico')
        Vid_paciente = request.form['txtidpaciente']
        Vfecha = request.form['txtfecha']
        Vnombre = request.form['txtnombre'] if 'txtnombre' in request.form else ""
        Vapellidos = request.form['txtapellidos'] if 'txtapellidos' in request.form else ""
        Vpeso = request.form['peso']
        Valtura = request.form['altura']
        Vtemperatura = request.form['temperatura']
        Vlatidos = request.form['latidos']
        Vsaturacion = request.form['saturacion']
        Vglucosa = request.form['glucosa']
        Vsintomas = request.form['txtsintomas']
        Vdiagnostico = request.form['txtdiagnostico']
        Vtratamiento = request.form['txttratamiento']
        Vsolicitud_estudios = request.form['txtsolicitud']
    
        if Vfecha == "" or Vpeso == "" or Valtura == "" or Vtemperatura == "" or Vlatidos == "" or Vsaturacion == "" or Vglucosa == "" or Vsintomas == "" or Vdiagnostico == "" or Vtratamiento == "" or Vsolicitud_estudios == "":
            flash('No se pueden guardar campos vacíos')
            cedula_medico = session.get('cedula_medico')
            CS = mysql.connection.cursor()
            CS.execute('select * from pacientes where cedulamedico = %s', (cedula_medico,))
            Consultas = CS.fetchall()
            return render_template('cesxploracion.html', listapacientes=Consultas)
        else:
            CScon = mysql.connection.cursor() 
            CScon.execute('INSERT INTO expacientes(cedulademedico, idpaciente, fecha, nombrepaciente, apellidospaciente, peso, altura, temperatura, latidos, saturacion, glucosa, sintomas, diagnostico, tratamiento, solicitudestudios) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                          (Vcedula, Vid_paciente, Vfecha, Vnombre, Vapellidos, Vpeso, Valtura, Vtemperatura, Vlatidos, Vsaturacion, Vglucosa, Vsintomas, Vdiagnostico, Vtratamiento, Vsolicitud_estudios))
            mysql.connection.commit()
            flash('La exploración y diagnóstico se guardó correctamente')    
            cedula_medico = session.get('cedula_medico')
            CSconsu = mysql.connection.cursor()
            CSconsu.execute('select * from pacientes where cedulamedico = %s', (cedula_medico,))
            Consultas = CSconsu.fetchall()
            return render_template('cesxploracion.html', listapacientes=Consultas)        

@app.route('/Consultacita')
def consultacita():
    cedula_medico = session.get('cedula_medico')
    CS = mysql.connection.cursor()
    CS.execute('select * from expacientes where cedulademedico = %s', (cedula_medico,))
    Consultas = CS.fetchall()
    return render_template('consultacita.html', listapacientes = Consultas)

@app.route('/Consultarcitapornombre', methods=['POST'])
@login_required
def Buscarcitapornombre():
    Varbuscar= request.form['txtbuscar']
    CCs= mysql.connection.cursor()
    CCs.execute('select * from expacientes where nombrepaciente LIKE %s', (f'%{Varbuscar}%',))
    consultapacs= CCs.fetchall()
    return render_template('consultacita.html', listapacientes = consultapacs)

@app.route('/Consultapacfecha', methods=['POST'])
@login_required
def consultapacfecha():
    fecha_buscar = request.form['fechaBuscar']
    try:
        fecha_convertida = datetime.strptime(fecha_buscar, '%Y-%m-%d')
    except ValueError:
        flash('Fecha inválida. Formato esperado: AAAA-MM-DD', 'error')
        return redirect('/Consultacita')

    CC = mysql.connection.cursor()
    CC.execute('SELECT * FROM expacientes WHERE fecha = %s', (fecha_convertida,))
    consultapac = CC.fetchall()
    return render_template('consultacita.html', listapacientes=consultapac)
    

#-------------------- Consultar paciente ------------------------------------------
@app.route('/Consultapaciente')
@login_required
def consultapaciente():
    cedula_medico = session.get('cedula_medico')
    CS = mysql.connection.cursor()
    CS.execute('select * from pacientes where cedulamedico = %s', (cedula_medico,))
    Consulta = CS.fetchall()
    return render_template('cpacientes.html', listapacientes = Consulta)

@app.route('/Consultapacnombre', methods=['POST'])
@login_required
def consultapacnombre():
    Varbuscar= request.form['txtbuscar']
    CC= mysql.connection.cursor()
    CC.execute('select * from pacientes where nombre LIKE %s', (f'%{Varbuscar}%',))
    consultapac= CC.fetchall()
    return render_template('cpacientes.html', listapacientes = consultapac)

#------------------------------ Editar paciente -------------------------------------------------------
@app.route('/Editarpaciente/<id>')
def editarpaciente(id):
    CSid = mysql.connection.cursor()
    CSid.execute('select * from pacientes where id = %s', (id,))
    Consultaid = CSid.fetchone()
    return render_template('apacientes.html', pac= Consultaid) 

@app.route('/actualizarpaciente/<id>', methods=['POST'])
@login_required
def actualizarpaciente(id):
    if request.method == 'POST':
        Vnombre = request.form['txtNombre']
        Vapellido = request.form['txtApellido']
        Vnacimiento = request.form['txtnacimiento']
        Venfermedades = request.form['txtenfermedades'] if 'txtenfermedades' in request.form else ""
        Valergias = request.form['txtalergias'] if 'txtalergias' in request.form else ""
        Vantecedentes = request.form['txtantecedentes'] if 'txtantecedentes' in request.form else ""
        #print(Vcedula, Vnombre, Vapellido, Vnacimiento, Venfermedades, Valergias, Vantecedentes)
        
        if Vnombre == "" or Vapellido =="" or Vnacimiento == "" or Venfermedades == "" or Valergias == "" or Vantecedentes == "":
            flash('No se pueden guardar campos vacíos')
            CSid = mysql.connection.cursor()
            CSid.execute('select * from pacientes where id = %s', (id,))
            Consultaid = CSid.fetchone()
            return render_template('apacientes.html', pac= Consultaid) 

        else:
            if Venfermedades == 'Otra':
                Venfermedadesotro = request.form['txtenfermedades_otro']
                if Venfermedadesotro == "":
                    flash('No se pueden guardar campos vacíos')
                    CSid = mysql.connection.cursor()
                    CSid.execute('select * from pacientes where id = %s', (id,))
                    Consultaid = CSid.fetchone()
                    return render_template('apacientes.html', pac= Consultaid) 
                else:
                    Venfermedades = Venfermedadesotro

            if Valergias == 'Otro':
                Valergiasotro = request.form['txtalergias_otro']
                if Valergiasotro == "":
                    flash('No se pueden guardar campos vacíos')
                    CSid = mysql.connection.cursor()
                    CSid.execute('select * from pacientes where id = %s', (id,))
                    Consultaid = CSid.fetchone()
                    return render_template('apacientes.html', pac= Consultaid) 
                else:
                    Valergias = Valergiasotro

            if Vantecedentes == 'Otro':
                Vantecedentesotro = request.form['txtantecedentes_otro']
                if Vantecedentesotro == "":
                    flash('No se pueden guardar campos vacíos')
                    CSid = mysql.connection.cursor()
                    CSid.execute('select * from pacientes where id = %s', (id,))
                    Consultaid = CSid.fetchone()
                    return render_template('apacientes.html', pac= Consultaid) 
                else:
                    Vantecedentes = Vantecedentesotro
            CS = mysql.connection.cursor()
            CS.execute('update pacientes set nombre= %s, apellidos= %s,fechanacimiento= %s,enfermedades= %s,alergias= %s,antecedentes= %s where id= %s', (Vnombre, Vapellido, Vnacimiento, Venfermedades, Valergias, Vantecedentes,id,))
            mysql.connection.commit()
            flash('El paciente se guardó correctamente')
            cedula_medico = session.get('cedula_medico')
            CS = mysql.connection.cursor()
            CS.execute('select * from pacientes where cedulamedico = %s', (cedula_medico,))
            Consulta = CS.fetchall()
            return render_template('cpacientes.html', listapacientes = Consulta)
        
# ------------------------------ Borrar -----------------------------------------------------------
@app.route('/borrarpaciente/<id>', methods=['POST'])
@login_required
def eliminarpaciente(id):
    if request.method == 'POST':
        CSeli = mysql.connection.cursor()
        CSeli.execute('delete from pacientes where id= %s',(id,))
        CSeli.execute('delete from expacientes where idpaciente= %s',(id,))
        mysql.connection.commit()
        return jsonify({'message': 'success'})
    return jsonify({'message': 'error'})

@app.route('/borrarexpaciente/<id>', methods=['POST'])
@login_required
def eliminarexpaciente(id):
    if request.method == 'POST':
        CSeli = mysql.connection.cursor()
        CSeli.execute('delete from expacientes where id= %s',(id,))
        mysql.connection.commit()
        return jsonify({'message': 'success'})
    return jsonify({'message': 'error'})
# ---------------------------------------------------------------------------------------------------

@app.route('/generareceta/<id>')
def generareceta(id):
    age=session['patient_age']
    cedula_medico = session.get('cedula_medico')
    cs = mysql.connection.cursor()
    cs.execute('SELECT * FROM expacientes where id = %s', (id,))
    data = cs.fetchall()
    CCmedico= mysql.connection.cursor()
    CCmedico.execute('select * from medicos where cedula=%s', (cedula_medico,))
    medicos= CCmedico.fetchall()
    
    csfecha = mysql.connection.cursor()
    csfecha.execute('SELECT * FROM expacientes where id = %s', (id,))
    datafecha = csfecha.fetchone()
    idpaciente = datafecha[2]
    
    CCpaciente = mysql.connection.cursor()
    CCpaciente.execute('select * from pacientes where id=%s', (idpaciente,))
    paciente = CCpaciente.fetchone()
    Vfechanacimiento = paciente[4]
    print(Vfechanacimiento)

    hoy = datetime.today()
    age = hoy.year - Vfechanacimiento.year - ((hoy.month, hoy.day) < (Vfechanacimiento.month, Vfechanacimiento.day))
    session['patient_age'] = age
    edadpac = session['patient_age']

    html_content = render_template('pdf.html', pacientes=data,edad=edadpac,med=medicos)

    response = Response(content_type='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename=receta.pdf'

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []

    # Convertir el HTML a PDF utilizando xhtml2pdf
    result = pisa.CreatePDF(html_content, dest=buffer)

    if not result.err:
        pdf_data = buffer.getvalue()
        buffer.close()

        response.data = pdf_data
        return response
    else:
        buffer.close()
        return "Error generando el PDF"


if __name__ == '__main__':
 app.run(port=5800,debug=True)