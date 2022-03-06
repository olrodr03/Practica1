"""
Olga Rodríguez Acevedo
"""

"""
PRIMERA VERSIÓN
---------------
Disponemos de NPROD productores, un consumidor y un almacén de capacidad 
limitada, concretamente de capacidad NPROD. 

Idea a seguir por este programa:
    Inicialmente los NPROD productores fabrican un elemento y lo almacenan en 
    sus respectivos huecos del almacén. A continuación, el consumidor se encarga
    de consumir el mínimo de dichos elementos y almacenarlo en una nueva lista.
    Seguidamente, el consumidor permanece quieto hasta que el productor del 
    elemento consumido anteriormente vuelve a producir otro elemento y a 
    almacenarlo en su hueco. De esta manera, el consumidor procedería a consumir 
    de nuevo el mínimo de los elementos del almacén, repitiendo así el proceso
    anterior. Este desarrollo se repite infinitas veces.
"""

from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore
from multiprocessing import current_process
from multiprocessing import Array
import random
import numpy as np

NPROD = 3 # Número de productores.

def productor(pid, almacen, empty, non_empty):
    dato = random.randint(0,5)
    while True:
        empty[pid].acquire() 
        dato += random.randint(0,5) # Elemento a introducir en el almacén.
        print (f"productor {current_process().name} produciendo")
        almacen[pid] = dato
        print (f"productor {current_process().name} almacenado {dato}")
        non_empty[pid].release()
        
def consumidor(almacen, empty, non_empty):
    for s in non_empty:
        s.acquire() # Bloqueamos los semáforos 'non_empty' hasta que cada uno de 
                    # los productores haya fabricado un elemento.
    print (f"consumidor {current_process().name} desalmacenando")
    elementos_ordenados = [] # Inicializamos la lista que al final de la ejecución 
                             # contendrá los elementos del almacén ordenados de 
                             # menor a mayor.
    while True:
        dato = np.amin(almacen) # Mínimo elemento del almacén.
        elementos_ordenados.append(dato)
        posicion = almacen[:].index(dato) # Posición del mínimo elemento del almacén.
        empty[posicion].release()
        print (f"consumidor {current_process().name} consumiendo {dato}")
        non_empty[posicion].acquire()
    print(elementos_ordenados)
  
def main():
    # Lista de semáforos, los cuales indican: El hueco del productor i en el 
    # almacén está vacío.
    empty = [BoundedSemaphore(1) for i in range (NPROD)] 
    # Lista de semáforos, los cuales indican: El hueco del productor i en el 
    # almacén NO está vacío.
    non_empty = [Semaphore(0) for i in range (NPROD)]
    almacen = Array('i', NPROD) # Inicializamos el almacén con NPROD ceros.
    prodlst = [Process(target = productor,
                        name = f'prod_{i}',
                        args = (i, almacen, empty, non_empty))
                for i in range(NPROD)]
    cons = [Process(target = consumidor,
                     name = f"cons_",
                     args = (almacen, empty, non_empty))]
    for p in prodlst + cons:
        p.start()
    for p in prodlst + cons:
        p.join()
           
if __name__ == '__main__':
    main()