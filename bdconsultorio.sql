create database bdconsultorio;
use bdconsultorio;
create table Pacientes(
	id int primary key auto_increment not null,
    nombre char(50) not null,
    p_apellido char(50) not null,
    s_apellido char(50) not null,
    fecha_nacimiento date not null,
    estado int default(0)
);

create table Enfermedades(
	id int primary key auto_increment not null,
    nombre char(100)
);

create table Diagnosticos(
	id int primary key auto_increment not null,
    clave int not null,
    fecha_diagnostico date,
    id_paciente int,
    id_enfermedad int,
    foreign key (id_paciente) references Pacientes(id),
    foreign key (id_enfermedad) references Enfermedades(id)
);

create table Consultorios(
	id int primary key auto_increment not null,
    nombre char(50) not null
);

create table Consultas(
	id int primary key auto_increment not null,
    fecha_consulta date not null,
    id_consultorio int,
    id_paciente int,
    foreign key (id_consultorio) references Consultorios(id),
    foreign key (id_paciente) references Pacientes(id)
);

create table Personal(
	id int primary key auto_increment not null,
    usuario char(50) not null,
    passw char(50) not null,
    nombre char(50) not null,
    p_apellido char(50) not null,
    s_apellido char(50) not null,
    fecha_nacimiento date not null
);

create table Personal_consultorios(
	id int primary key auto_increment not null,
    fecha_asignacion date,
    id_consultorio int,
    id_personal int,
    foreign key (id_consultorio) references Consultorios(id),
    foreign key (id_personal) references Personal(id)
);