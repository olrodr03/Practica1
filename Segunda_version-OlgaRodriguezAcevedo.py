"""
Olga Rodríguez Acevedo
"""

"""
SEGUNDA VERSIÓN
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
    anterior. 
    Debemos tener en cuenta que cada uno de los productores únicamente podrá
    producir N elementos. En el momento en el que cada uno de ellos haya 
    producido su número máximo de elementos, añadirá el elemento '-1' en su 
    respectivo hueco del almacén.
"""

from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore
from multiprocessing import current_process
from multiprocessing import Array
import random

N = 2  # Cantidad de elementos que puede fabricar cada productor.
NPROD = 3 # Número de productores.

def productor(pid, almacen, empty, non_empty):
    dato = random.randint(0,5)
    for n in range(N):
        empty[pid].acquire()
        dato += random.randint(0,5) # Elemento a introducir en el almacén.
        print (f"productor {current_process().name} produciendo")
        almacen[pid] = dato
        print (f"productor {current_process().name} almacenado {dato}")
        non_empty[pid].release()
    print(f"producer {current_process().name} Ha terminado de producir") 
    empty[pid].acquire()
    almacen[pid] = -1 # Cuando el productor 'pid' haya fabricado su máximo número de
                      # elementos, añadimos el elemento '-1' en su hueco del almacén.
    non_empty[pid].release()

def consumidor(almacen, empty, non_empty):
    for s in non_empty:
        s.acquire() # Bloqueamos los semáforos 'non_empty' hasta que cada uno de 
                    # los productores haya fabricado un elemento.
    print (f"consumidor {current_process().name} desalmacenando")
    running = [True for _ in range (NPROD)] # Lista que nos indicará:
                                            # ·'True' si el productor i puede producir más elementos.
                                            # ·'False' si el productor i ya NO puede producir más elementos.
    elementos_ordenados = [] # Inicializamos la lista que al final de la ejecución 
                             # contendrá los elementos del almacén ordenados de 
                             # menor a mayor.
    while True in running:
        numeros = []
        for i in range(NPROD):
            running[i] = almacen[i]>=0
            if running[i]:
                numeros.append(almacen[i])
        if numeros == []:
            break
        dato = min(numeros) # Mínimo elemento del almacén.
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