from datetime import *
timeActual = datetime.now()
# formatoTime = timeActual.strftime("%Y-%m-%d")
# print(formatoTime)
# fecha2 = datetime(2006, 1, 20)
# diferencia = (timeActual - fecha2).days
# diferenciaAN = diferencia / 365
# print(diferencia)
# print(diferenciaAN)
# if diferenciaAN > 18:
#     print("Ya esta grande")
    
fecha1 = ('2006-01-20')
year, month, day = map(int, fecha1.split('-'))
fechaInt = datetime(year, month, day)
print((year, month, day))
diferencia = (timeActual - fechaInt).days
diferenciaAN = diferencia / 365
print(diferenciaAN)
# if formatoTime < '2024-01-20':
#     print("Menor")
# else:
#     print("Mayor")

year, month, day = map(int, fecha1.split('-'))
fechaInt = datetime(year, month, day)
diferencia = (timeActual - fechaInt).days
diferenciaAN = diferencia / 365