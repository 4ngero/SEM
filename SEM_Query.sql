create database SEM;
use SEM;
create table Pacientes(
	id int primary key auto_increment not null,
    nombre char(50) not null,
    p_apellido char(50) not null,
    s_apellido char(50) not null,
    fecha_nacimiento date not null,
    estado int default(0),
    sexo char(20)
);
select * from Pacientes;

create table Enfermedades(
	id int primary key auto_increment not null,
    nombre char(100)
);
select * from Enfermedades;

create table Diagnosticos(
	id int primary key auto_increment not null,
    clave int not null,
    fecha_diagnostico date,
    id_paciente int,
    id_enfermedad int,
    foreign key (id_paciente) references Pacientes(id),
    foreign key (id_enfermedad) references Enfermedades(id)
);
select * from Diagnosticos;

create table Consultorios(
	id int primary key auto_increment not null,
    nombre char(50) not null
);
select * from Consultorios;

create table Consultas(
	id int primary key auto_increment not null,
    fecha_consulta date,
    id_consultorio int,
    id_paciente int,
    foreign key (id_consultorio) references Consultorios(id),
    foreign key (id_paciente) references Pacientes(id)
);
select * from Consultas;

alter table Consultas drop column fecha_consulta;
select * from Consultas;
alter table Consultas add column (fecha_consulta date);

create table Personal(
	id int primary key auto_increment not null,
    usuario char(50) not null,
    passw char(50) not null,
    nombre char(50) not null,
    p_apellido char(50) not null,
    s_apellido char(50) not null,
    fecha_nacimiento date not null
);
select * from Personal;

create table Personal_consultorios(
	id int primary key auto_increment not null,
    fecha_asignacion date,
    id_consultorio int,
    id_personal int,
    foreign key (id_consultorio) references Consultorios(id),
    foreign key (id_personal) references Personal(id)
);
select * from Personal_consultorios;

insert into Personal_consultorios(fecha_asignacion, id_consultorio, id_personal)
	values	('2024-01-25', 2, 2);
    
select P.nombre from Pacientes as P 
inner join Consultas as C on P.id=C.id_paciente
inner join Consultorios as Co on Co.id=C.id_consultorio
inner join Personal_consultorios as Pc on Co.id=Pc.id_consultorio
inner join Personal as Pe on P.id=PC.id_personal where P.id = 9;

insert into Personal(usuario, passw, nombre, p_apellido, s_apellido, fecha_nacimiento)
	values	('123456789', '321', 'Axel', 'Albani', 'Gutierrez', '1999-11-14');

insert into Consultorios(nombre)
	values	('Consultorio 1'),
			('Consultorio 2'),
            ('Consultorio 2');
select * from Personal;
select * from Pacientes;
select * from Consultas;