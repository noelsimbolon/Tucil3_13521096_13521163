import customtkinter
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.algorithm.main_algorithm import Engine
from src.gui import util
from src.io.file_handler import FileInputHandler
from src.model.node import Node


class FileTab(customtkinter.CTkFrame):
    # Algorithm arguments
    starting_index: int = 0
    destination_index: int = 0
    nodes: list[Node] = []  # List of available Nodes
    adj_matrix: list[list[float]] = [[]]  # Two-dimensional list to hold the adjacency matrix

    # Output
    route: list[Node] = []  # List of route Nodes
    distance: float = 0

    # Attribute to save node positions in the graph visualization
    input_graph: nx.Graph = None
    node_positions: dict = {}

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        button_font = customtkinter.CTkFont(family='Segoe UI', size=-13, weight='bold')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.file_input_frame = FileInputFrame(master=self, width=180)
        self.file_input_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky='nswe')

        # Open file button
        self.open_file_button = customtkinter.CTkButton(master=self.file_input_frame,
                                                        text='Open File',
                                                        font=button_font,
                                                        command=self.parse_file_and_visualize_input_graph)
        self.open_file_button.grid(row=1, column=0, padx=20, pady=(10, 0))

        # Start button
        self.start_button = customtkinter.CTkButton(master=self.file_input_frame,
                                                    text='Start',
                                                    font=button_font,
                                                    command=self.find_shortest_route_and_visualize_route)
        self.start_button.grid(row=9, column=0, padx=20, pady=(10, 0))

        self.file_output_frame = FileOutputFrame(master=self)
        self.file_output_frame.grid(row=0, column=1, padx=(5, 10), pady=10, sticky='nswe')

    def parse_file_and_visualize_input_graph(self) -> None:
        # Clear any text output first
        self.file_input_frame.file_validation_message.configure(text='')
        self.file_input_frame.status_message.configure(text='')

        try:
            FileTab.parse_file()
        except FileNotFoundError:
            self.file_input_frame.file_validation_message.configure(text='Please open a file.',
                                                                    text_color='red')
            return
        except RuntimeError:
            self.file_input_frame.file_validation_message.configure(text='Invalid file.',
                                                                    text_color='red')
            return

        if len(FileTab.nodes) < 8:
            self.file_input_frame.file_validation_message.configure(text='Minimum 8 nodes required.',
                                                                    text_color='red')
            return

        self.visualize_input_graph()

    @staticmethod
    def parse_file() -> None:
        file_path = customtkinter.filedialog.askopenfilename(title='Open a Text File',
                                                             filetypes=[("Text Files", "*.txt")])
        nodes, adj_matrix = FileInputHandler.load_file(file_path)

        FileTab.nodes = nodes
        FileTab.adj_matrix = adj_matrix

    def visualize_input_graph(self) -> None:
        num_nodes = len(FileTab.adj_matrix)

        # Create an empty graph
        FileTab.input_graph = nx.Graph()

        # Add nodes to the graph
        FileTab.input_graph.add_nodes_from([node.node_id for node in FileTab.nodes])

        # Add edges to the graph based on the adjacency matrix (testing)
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):  # Only iterate over the upper triangle of the matrix to avoid duplicates
                weight = FileTab.adj_matrix[i][j]
                if weight > 0:
                    FileTab.input_graph.add_edge(i, j, weight=weight)  # Add edge with weight as an attribute

        # Compute the spring layout for node positions
        FileTab.node_positions = nx.spring_layout(FileTab.input_graph)

        # Create a Figure object
        fig = plt.figure(figsize=(7, 4))  # Width and height in inches

        # Remove black borders
        ax = fig.gca()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        # Draw nodes
        nx.draw_networkx_nodes(FileTab.input_graph, pos=FileTab.node_positions)

        # Draw edges
        nx.draw_networkx_edges(FileTab.input_graph, pos=FileTab.node_positions)

        # Draw node labels
        nx.draw_networkx_labels(FileTab.input_graph, pos=FileTab.node_positions)

        # Destroy graph canvas (if a plot is present this destroys it)
        self.file_output_frame.graph_canvas.get_tk_widget().destroy()

        # Visualize the graph
        self.file_output_frame.graph_canvas = FigureCanvasTkAgg(fig, master=self.file_output_frame.graph_frame)
        self.file_output_frame.graph_canvas.draw()
        self.file_output_frame.graph_canvas.get_tk_widget().pack()

        self.file_input_frame.file_validation_message.configure(text='Graph visualized.', text_color='green')

    def find_shortest_route_and_visualize_route(self) -> None:
        # If the user hasn't opened a file
        if len(FileTab.nodes) == 0:
            # Clear status message
            self.file_input_frame.status_message.configure(text="")
            self.file_input_frame.status_message.configure(text="Please open a file first.",
                                                           text_color='red')
            return

        # If the starting node index or the destination node index is not valid,
        # display error message until it is valid
        if not (FileTab.is_index_valid(self.file_input_frame.starting_node_entry.get()) and
                FileTab.is_index_valid(self.file_input_frame.destination_node_entry.get())):

            # Clear status message
            self.file_input_frame.status_message.configure(text="")

            # If the starting node index is not valid
            if not FileTab.is_index_valid(self.file_input_frame.starting_node_entry.get()):
                self.file_input_frame.status_message.configure(text="Invalid starting node.",
                                                               text_color='red')
                return
            else:
                self.file_input_frame.status_message.configure(text="")

            # If the destination node index is not valid
            if not FileTab.is_index_valid(self.file_input_frame.destination_node_entry.get()):
                self.file_input_frame.status_message.configure(text="Invalid destination node.",
                                                               text_color='red')
                return
            else:
                self.file_input_frame.status_message.configure(text="")

        try:
            self.find_shortest_route()
        except TypeError:
            # There is no route from the starting node to the destination node
            self.file_input_frame.status_message.configure(text="No route found.",
                                                           text_color='red')
            return

        self.visualize_route()
        self.show_route_and_distance()

    def find_shortest_route(self) -> None:
        FileTab.starting_index = int(self.file_input_frame.starting_node_entry.get())
        FileTab.destination_index = int(self.file_input_frame.destination_node_entry.get())

        # Start algorithm
        if self.file_input_frame.algorithm_options.get() == 'A*':
            # A-star path-finding
            FileTab.distance, FileTab.route = Engine.search_astar(FileTab.starting_index,
                                                                  FileTab.destination_index,
                                                                  FileTab.nodes,
                                                                  FileTab.adj_matrix)
        else:
            # UCS path-finding
            FileTab.distance, FileTab.route = Engine.search_ucs(FileTab.starting_index,
                                                                FileTab.destination_index,
                                                                FileTab.nodes,
                                                                FileTab.adj_matrix)

    def visualize_route(self) -> None:
        fig = plt.figure(figsize=(7, 4))

        # List of node IDs to color edges between
        route_nodes = [node.node_id for node in FileTab.route]

        # Iterate over edges to get the edges that needs to be colored yellow
        route_edges = []
        i = 0
        while i < len(route_nodes) - 1:
            for edge in FileTab.input_graph.edges():
                if i + 1 < len(route_nodes):
                    if (edge[0] == route_nodes[i] and edge[1] == route_nodes[i + 1]) or \
                            (edge[1] == route_nodes[i] and edge[0] == route_nodes[i + 1]):
                        route_edges.append(edge)
                        i += 1
                else:
                    break

        # Color the route edges yellow
        for edge in FileTab.input_graph.edges():
            if edge in route_edges:
                FileTab.input_graph.edges[edge]['edge_color'] = 'yellow'
            else:
                FileTab.input_graph.edges[edge]['edge_color'] = 'black'

        # Draw nodes
        nx.draw_networkx_nodes(FileTab.input_graph, pos=FileTab.node_positions)

        # Draw edges
        nx.draw_networkx_edges(FileTab.input_graph, pos=FileTab.node_positions)

        # Draw node labels
        nx.draw_networkx_labels(FileTab.input_graph, pos=FileTab.node_positions)

        # Draw the graph with edge colors
        edge_colors = [FileTab.input_graph.edges[edge]['edge_color'] for edge in FileTab.input_graph.edges()]
        nx.draw(FileTab.input_graph, pos=FileTab.node_positions, with_labels=True, edge_color=edge_colors)

        # Destroy graph canvas (if a plot is present this destroys it)
        self.file_output_frame.graph_canvas.get_tk_widget().destroy()

        # Visualize the graph
        self.file_output_frame.graph_canvas = FigureCanvasTkAgg(fig,
                                                                master=self.file_output_frame.graph_frame)
        self.file_output_frame.graph_canvas.draw()
        self.file_output_frame.graph_canvas.get_tk_widget().pack()

        self.file_input_frame.status_message.configure(text='Route visualized.',
                                                       text_color='green')

    def show_route_and_distance(self) -> None:
        # Convert the route to string, example: 2-1-6-3-7
        route = ''
        for route_node in FileTab.route:
            route += f'{route_node.node_id}-'
        route = route[:-1]  # Remove trailing hyphen

        self.file_output_frame.result_tab_view.route_label.configure(text=route)
        self.file_output_frame.result_tab_view.distance_label.configure(text=f'{FileTab.distance:.5f} m')

    @staticmethod
    def is_index_valid(index: int) -> bool:
        """
        Validates the node index
        :param index: node's index
        :return: True if the index is valid, False otherwise
        """
        try:
            if 0 <= int(index) <= len(FileTab.adj_matrix) - 1:
                return True
        except ValueError:
            return False

        return False


class FileInputFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Custom-defined fonts
        title_font = customtkinter.CTkFont(family='Segoe UI', size=-18, weight='bold')
        message_font = customtkinter.CTkFont(family='Segoe UI', size=-13, weight='normal')
        input_label_font = customtkinter.CTkFont(family='Segoe UI', size=-13, weight='bold')
        entry_font = customtkinter.CTkFont(family='Segoe UI', size=-13, weight='normal')
        select_theme_font = customtkinter.CTkFont(family='Segoe UI', size=-13, weight='normal')
        select_algorithm_font = customtkinter.CTkFont(family='Segoe UI', size=-13, weight='normal')

        # Expandable empty space between the Start button and UI theme options
        self.grid_rowconfigure(11, weight=1)

        # App title
        self.app_title = customtkinter.CTkLabel(master=self,
                                                text='Compass',
                                                font=title_font)
        self.app_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Input file button is defined in FileTab

        self.file_validation_message = customtkinter.CTkLabel(master=self,
                                                              text='',
                                                              font=message_font)
        self.file_validation_message.grid(row=2, column=0, padx=20, pady=0)

        # Starting node and destination node
        self.starting_node_label = customtkinter.CTkLabel(master=self,
                                                          text='Starting node:',
                                                          font=input_label_font)
        self.starting_node_label.grid(row=3, column=0, padx=20, pady=0)

        self.starting_node_entry = customtkinter.CTkEntry(master=self,
                                                          placeholder_text="Node number",
                                                          font=entry_font)
        self.starting_node_entry.grid(row=4, column=0, padx=20, pady=0)

        self.destination_node_label = customtkinter.CTkLabel(master=self,
                                                             text='Destination node:',
                                                             font=input_label_font)
        self.destination_node_label.grid(row=5, column=0, padx=20, pady=0)

        self.destination_node_entry = customtkinter.CTkEntry(master=self,
                                                             placeholder_text="Node number",
                                                             font=entry_font)
        self.destination_node_entry.grid(row=6, column=0, padx=20, pady=(0, 5))

        # Select algorithm
        self.select_algorithm_label = customtkinter.CTkLabel(master=self,
                                                             text="Select algorithm:",
                                                             font=input_label_font)
        self.select_algorithm_label.grid(row=7, column=0, padx=20, pady=(5, 0))

        self.algorithm_options = customtkinter.CTkOptionMenu(master=self,
                                                             values=['A*', 'UCS'],
                                                             font=select_algorithm_font)
        self.algorithm_options.grid(row=8, column=0, padx=20, pady=(0, 10))

        # Start button is defined in FileTab

        self.status_message = customtkinter.CTkLabel(master=self,
                                                     text='',
                                                     font=message_font)
        self.status_message.grid(row=10, column=0, padx=20, pady=0)

        # Select GUI theme
        self.select_theme_label = customtkinter.CTkLabel(master=self,
                                                         text="Select theme:",
                                                         font=select_theme_font)
        self.select_theme_label.grid(row=12, column=0, padx=20, pady=0)

        self.theme_options = customtkinter.CTkOptionMenu(master=self,
                                                         values=["Dark", "Light", "System"],
                                                         font=select_theme_font,
                                                         command=util.change_appearance_mode)
        self.theme_options.grid(row=13, column=0, padx=20, pady=(0, 20))


class FileOutputFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Configure the grid system
        self.grid_rowconfigure((0, 2), weight=1)
        self.grid_columnconfigure((0, 2), weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(3, weight=0)

        # Transparent frame to hold the graph visualization
        self.graph_frame = customtkinter.CTkFrame(master=self,
                                                  fg_color='transparent')
        self.graph_frame.grid(row=1, column=1)

        # Initialize a canvas for graph visualization
        # This initialization is useful to avoid displaying multiple plots
        # by destroying the canvas before creating a new one every time a graph is want to be drawn
        self.graph_canvas = FigureCanvasTkAgg(None, master=self.graph_frame)

        # Result tab view
        self.result_tab_view = FileResultTabView(master=self,
                                                 height=125)
        self.result_tab_view.grid(row=3, column=0, columnspan=3, padx=20, pady=20, sticky='we')
        self.result_tab_view._segmented_button.configure(font=('Segoe UI', -13, 'bold'))


class FileResultTabView(customtkinter.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        output_font = customtkinter.CTkFont(family='Segoe UI', size=-14, weight='normal')

        # Create two tabs for output
        self.add('Route')
        self.add('Distance')

        self.tab('Route').grid_columnconfigure(0, weight=1)
        self.tab('Distance').grid_columnconfigure(0, weight=1)

        # Create a scrollable frame to hold the route
        self.route_scrollable_frame = customtkinter.CTkScrollableFrame(master=self.tab('Route'),
                                                                       height=30,
                                                                       orientation='horizontal')
        self.route_scrollable_frame.grid(row=0, column=0, columnspan=1, pady=10, sticky='ns')

        self.route_label = customtkinter.CTkLabel(master=self.route_scrollable_frame,
                                                  text='',
                                                  text_color='green',
                                                  font=output_font)
        self.route_label.grid(row=0, column=0, padx=10)

        # Create a label for distance
        self.distance_label = customtkinter.CTkLabel(master=self.tab('Distance'),
                                                     text='',
                                                     text_color='green',
                                                     font=output_font)
        self.distance_label.grid(row=0, column=0, pady=(20, 0))
