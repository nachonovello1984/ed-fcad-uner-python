from typing import Any, List, Dict, Set, Generator
from .vertex import Vertex
from .edge import Edge


class Graph:
    """ Implementación de un grafo simple utilizando mapeo de adyacencia."""

    #########################################################################
    #							MÉTODOS PÚBLICOS
    #########################################################################

    def __init__(self, is_directed: bool) -> None:
        """ Configura una nueva instancia de Graph con dos diccionarios Python.
        Si el grafo es dirigido los dos diccionarios serán diferentes,
        caso contrario uno es un alias del otro (). Es decir, son referencias al
        mismo objeto diccionario.

        Args:
            is_directed (bool): Indica si el grafo es dirigido o no.
        """
        self._outgoing: Dict[Vertex, Dict[Vertex, Edge]] = {}
        self._incoming: Dict[Vertex, Dict[Vertex, Edge]] = {} if is_directed else self._outgoing

    def __str__(self) -> str:
        """_summary_

        Returns:
            str: _description_
        """
        if not self.vertex_count():
            return "Graph()"

        res = ""

        for v in self._outgoing.keys():
            res += f"\n  -> {str(v)}: { [str(edge) for edge in self._outgoing[v].values()] }" + "\n"

        return f"Graph():{res}"

    def is_directed(self) -> bool:
        """ Indica si el grafo es dirigido o no.

        Returns:
            bool: True si _incoming  referencia al mismo objeto que referencia _outgoing.
        """
        return self._incoming is not self._outgoing

    def vertex_count(self) -> int:
        """ Devuelve la cantidad de vértices del grafo.

        Returns:
            int: devuelve la cantidad de vértices del grafo.
        """
        return len(self._outgoing.keys())
    
    def vertices(self) -> List[Any]:
        """ Devuelve una lista con todos los vértices del grafo.

        Returns:
            List[Any]: Lista formada por todos los vértices del grafo.
        """
        return [key for key in self._outgoing.keys()]

    def edge_count(self) -> int:
        """ Devuelve la cantidad de arcos del grafo.

        Returns:
            int: devuelve la cantidad de vértices del grafo.
        """
        # Suma la cantidad de items en el diccionario outgoing para cada uno de los vértices.
        total = sum(len(self._outgoing[v]) for v in self._outgoing)
        # Si el grafo es dirigido entonces devuelve el total calculado en la línea anterior.
        # En caso que el grafo sea no dirigido, nos aseguramos de no contar dos veces los vértices.
        return total if self.is_directed() else total // 2

    def edges(self) -> Set[Edge]:
        """ Devuelve todos los arcos del grafo.

        Returns:
            Set[Edge]: Evita la repetición de arcos utilizando un conjunto.
        """
        # En un grafo no dirigido evita informar dos veces los arcos.
        result: Set[Edge] = set()

        # Para cada uno de los vértices, toma los arcos y los
        for secondary_map in self._outgoing.values():
            #
            result.update(secondary_map.values())

        return result

    def get_edge(self, u: Vertex, v: Vertex) -> Edge:
        """ Devuelve el arco que conecta u y v.

        Args:
            u (Vertex): vértice origen
            v (Vertex): vértice destino

        Returns:
            Edge: arco que conecta u y v (en ese órden)
        """
        # Siempre busco en _outgoing en el órden de los parámetros.
        return self._outgoing[u].get(v)   # type: ignore

    def degree(self, v: Vertex, outgoing: bool = True) -> int:
        """ Devuelve la cantidad de arcos entrantes/salientes de v.

        Args:
            v (Vertex): vértice del cuál se analizarán la cantidad de arcos.
            outgoing (bool, optional): True si se tendrán en cuenta los arcos de salida.
            Caso contrario los de entrada. Valor por defecto True.

        Returns:
            int: número de arcos que entran/salen de v.
        """
        # Determino el diccionario sobre el que hacer el análisis y se lo asigno a adj.
        adj = self._outgoing if outgoing else self._incoming

        # Devuelvo la cantidad de entradas en el diccionario.
        return len(adj[v])

    def incident_edges(self, v: Vertex, outgoing: bool = True) -> Generator[Edge, None, None]:
        """ Devuelve un generator con todos los arcos que entran / salen de v.

        Args:
            v (Vertex): vértice del que se quieren obtener los arcos
            outgoing (bool, optional): True si se quieren obtener los arcos que salen de v.
            Caso contrario los de entrada. Valor por defecto True.

        Yields:
            Generator[Edge, None, None]: devuelve generator con todos los arcos que entran/salen de v.
        """
        # Determino el diccionario sobre el que se quiere hacer el análisis.
        adj = self._outgoing if outgoing else self._incoming

        # Obtengo todos los arcos del diccionario referenciado por adj.
        for edge in adj[v].values():
            yield edge

    def insert_vertex(self, x: Any) -> Vertex:
        """ Crea un vértice x en el grafo y lo devuelve.

        Args:
            x (Any | None, optional): _description_. Defaults to None.

        Returns:
            Vertex: _description_
        """
        # Creo el vértice
        v = Vertex(x)
        # Defino un diccionario para v en _outgoing.
        self._outgoing[v] = {}
        # Si el grafo es dirigido hago lo mismo en _incoming.
        if self.is_directed():
            self._incoming[v] = {}
        # Devuelvo v.
        return v

    def insert_edge(self, u: Vertex, v: Vertex, x: Any | None) -> None:
        """ Inserta un arco entre con origen u, destino v y elemento x.

        Args:
            u (Vertex): vértice origen.
            v (Vertex): vértice destino.
            x (Any | None): información a almacenar en el arco.
        """
        # Creo el arco
        e = Edge(u, v, x)
        # Lo registro en _outgoing e _incoming.
        self._outgoing[u][v] = e
        self._incoming[v][u] = e

    def dfs(self, u: Vertex) -> Dict[Vertex, Edge | None]:
        """ Realiza una búsqueda primero en profundidad (DFS) el el grafo comenzando por el nodo u.

        Args:
            u (Vertex): vértice por donde comenzar la búsqueda.

        Returns:
            Dict [Vertex, Edge | None]: Diccionario resultante con el camino compuesto por los vértices visitados.
        """
        # Defino un diccionario (que va a ser el resultado) con u como vértice donde comienza el recorrido.
        result: Dict[Vertex, Edge | None] = {u: None}
        # Hago el recorrido quedando el resultado en result.
        self._dfs(u, result)
        # Retorno result.
        return result

    def construct_path(self, u: Vertex, v: Vertex, discovered: Dict[Vertex, Edge]) -> List[Vertex]:
        """Devuelve una lista con los vértices pertenecientes al camino desde u a v ó
        una lista vacía si v no es alcanzable desde u.
        
        Args:
            u (Vertex): vértice al principio del camino.
            v (Vertex): vértice al final del camino.
            discovered (Dict[Vertex, Edge]): es el diccionario resultante de una llamada previa a dfs iniciada en u.

        Returns:
            List[Vertex]: camino de u a v.
        """
        path : List[Vertex] = []

        if v in discovered:
            
            path.append(v) # Construímos una lista desde v hasta u y luego la invertimos al final del algoritmo.
            walk = v # Definimos v como walk.
            
            while walk is not u: # Si walk no es u
                e = discovered[walk] # Obtenemos el arco para walk.
                parent = e.opposite(walk) # Pido el opuesto a walk en el arco e.
                path.append(parent) # Lo agrego a la lista resultado.
                walk = parent # Ahora parent es el nuevo walk.
                
            path.reverse() # Invierto la lista resultado.
            
        return path
    
    def dfs_complete(self) -> Dict[Vertex, Edge | None]:
        """ Lleva a cabo una búsqueda primero en profundidad para todo el grafo y 
        retorna el diccionario forest. El resultado mapea cada vértice al arco que 
        fue usado para descubrirlo. Los vértices que mapean a None son las raíces 
        del árbol DFS.

        Returns:
            Dict[Vertex, Edge | None]: Diccionario resultado que mapea el vértice junto con el arco que se utilizó para descubrirlo.
        """
        forest : Dict[Vertex, Edge | None] = {}
        # Obtengo una lista con todos los vértices del grafo y los proceso uno a uno.
        for u in self.vertices():
            # Si ya no lo encontré
            if u not in forest:
                # Indico que hay que comenzar una nueva DFS a partir de u.
                forest[u] = None
                self._dfs(u, forest)
        return forest
        
    
    #########################################################################
    #							MÉTODOS NO PÚBLICOS
    #########################################################################
        
    def _dfs(self, u : Vertex, discovered : Dict[Vertex, Edge | None]) -> None:
        """ Realiza la búsqueda utilizando un algoritmo recursivo y dejando los nodos 
        visitados en discovered.

        Args:
            u (Vertex): vértice sobre el que se van a analizar los arcos.
            discovered (Dict[Vertex, Edge]): camino con todos los nodos ya visitados.
        """
        # Para el vértice u obtengo los arcos.
        for e in self.incident_edges(u):
            # Obtengo el vértice opuesto a u para el arco e
            v = e.opposite(u)
            # Si v no estaba en el diccionario de los vértices visitados.
            if v not in discovered:
                # Lo inserto en discovered.
                discovered[v] = e
                # Recursivamente continúo haciendo la búsqueda por v.
                self._dfs(v, discovered)