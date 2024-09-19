# Install and load required packages
if (!requireNamespace("igraph", quietly = TRUE)) {
  install.packages("igraph")
}
library(igraph)

# Create a simple graph
nodes <- c("A", "B", "C", "D", "E")
edges <- c("A", "B", "B", "C", "C", "D", "D", "E", "E", "A")
graph <- graph(edges, directed = FALSE)
 tt<- 762
 
# Plot the graph
plot(graph, 
     vertex.color = "lightblue", 
     vertex.size = 40, 
     vertex.label.color = "black", 
     edge.color = "gray", 
     main = "Simple Graph using igraph")
