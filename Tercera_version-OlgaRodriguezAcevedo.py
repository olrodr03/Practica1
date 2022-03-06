"""
Olga Rodríguez Acevedo
"""

"""
TERCERA VERSIÓN
---------------
Disponemos de NPROD productores, un consumidor y un almacén de capacidad no fija. 

Idea a seguir por este programa:
    Inicialmente los NPROD productores fabrican un elemento y lo almacenan en 
    el almacén. A continuación, el consumidor se encarga de consumir el mínimo 
    de dichos elementos y almacenarlo en una nueva lista, al mismo tiempo que 
    los productores pueden seguir fabricando elementos y almacenándolos. 
    El consumidor permanecerá quieto hasta que en el almacén haya, como mínimo,
    un elemento fabricado por cada uno de los productores, momento en el que 
    volverá a consumir el mínimo de los elementos del almacén siguiendo el 
    proceso citado anteriormente.
    Debemos tener en cuenta que cada uno de los productores únicamente podrá
    fabricar N elementos y tener almacenados al mismo tiempo K elementos. 
"""

from multiprocessing import Process, Manager
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Array
from time import sleep
import random

N = 3 # Cantidad de elementos que puede fabricar cada productor.
K = 2 # Cantidad máxima de elementos que cada uno de los productores puede 
      # tener almacenados en el almacén.
NPROD = 3 # Número de productores.
  
def add_data(almacen, pid, dato, mutex):
    mutex.acquire()
    try:
        almacen.append(pid * 1000 + dato)
        sleep(1)
    finally:
        mutex.release()

def productor(almacen, pid, empty, non_empty, mutex):
    dato = random.randint(0,5)
    for n in range(N):
        empty[pid].acquire()
        dato += random.randint(0,5) # Elemento a introducir en el almacén.
        print (f"productor {current_process().name} produciendo")
        add_data(almacen, pid, dato, mutex) # Añadimos dicho elemento en el almacén.
        print (f"productor {current_process().name} almacenado {dato}")
        non_empty[pid].release()  
    print(f"producer {current_process().name} Ha terminado de producir") 
    empty[pid].acquire()
    sleep(1)
    non_empty[pid].release()
    
def consumidor(almacen, empty, non_empty, mutex):
    for s in non_empty:
        s.acquire() # Bloqueamos los semáforos 'non_empty' hasta que cada uno de 
                    # los productores haya fabricado un elemento.
    print (f"consumidor {current_process().name} desalmacenando")
    sleep(1)
    elementos_ordenados = [] # Inicializamos la lista que al final de la ejecución 
                             # contendrá los elementos del almacén ordenados de 
                             # menor a mayor.
    while len(elementos_ordenados) < NPROD * N:
        numeros = []
        lista_posicion = []
        for i in range(len(almacen)):
            if almacen[i] >= 0:
                numeros.append(almacen[i] % 1000)
                lista_posicion.append(almacen[i]//1000)
        if numeros == []:
            break
        dato = min(numeros) # Mínimo elemento del almacén.
        posicion = lista_posicion[numeros.index(dato)]
        posicion_almacen = almacen[:].index(dato + posicion * 1000) # Posición del mínimo 
                                                                    # elemento del almacén.
        almacen[posicion_almacen]= -2
        elementos_ordenados.append(dato)
        empty[posicion].release()
        print (f"consumidor {current_process().name} consumiendo {dato}")
        non_empty[posicion].acquire() 
    print(elementos_ordenados)

def main():
    manager = Manager()
    almacen = manager.list() # Inicializamos el almacén vacío.
    # Lista de semáforos, los cuales indican: El hueco del productor i en el 
    # almacén está vacío.
    empty = [BoundedSemaphore(K) for _ in range (NPROD)]
    # Lista de semáforos, los cuales indican: El hueco del productor i en el 
    # almacén NO está vacío.
    non_empty = [Semaphore(0) for i in range (NPROD)]
    mutex = Lock() # Exclusión mutua (semáforo)
    prodlst = [Process(target = productor,
                        name = f'prod_{i}',
                        args = (almacen, i, empty, non_empty, mutex))
                for i in range(NPROD)]
    cons = [Process(target = consumidor,
                      name = f"cons_",
                      args = (almacen, empty, non_empty, mutex))]
    for p in prodlst + cons:
        p.start()
    for p in prodlst + cons:
        p.join()

if __name__ == '__main__':
    main()