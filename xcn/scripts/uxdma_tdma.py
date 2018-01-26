#!/usr/bin/env python

# The TDMA algorithm used in this paper is based off the UxDMA framework described in [1].
#
# [1] S.Ramanathan. "A unified framework and algorithm for channel assignment in
#     wireless networks." BBN Technologies Division, GTE Internetworking,
#     Published in Wireless Networks 5 (1999) 91-94.

# This script implements a simplified version of UxDMA. Bi-directional links
# are assumed. The purpose of this script is to assign TDMA broadcast slots to
# each vertex (problem set 3 in UxDMA paper). The constraints used are Vtr^0
# and Vtt^1 (distance-2).
#
# We use the Progressive Minimum Neighbors First (PMNF) algorithm for choosing
# the order to select vertices for our coloring scheme. This is similiar to
# Minimum Neighbors First (MNF), where vertices which have the smallest number
# of edges are assigned a smaller label. The difference is that after labelling
# a vertex, this vertex and the edges incident on this vertex are ignored while
# processing the rest of the vertices.
#
# A key addition added to this implementation is to use PMNF ordering to
# distributed "unused" slots after the initial UxDMA algorithm is run. If N is
# the largest color value assigned, we attempt to give each vertex access to an
# additional color in a greedy fashion by checking if the color is allowed by
# the vertex's constraints. The difference with the PMNF implementation here is
# rather than ordering vertices purely based on the number of edges, we divide
# the number of edges by the number of colors assigned to the vertex. This
# allows for a more fair distribution of colors since pure PMNF could
# potentionally assign all slots to a single node with the most edges.


class UXDMA_TDMA:

  # Sorting function expecting values of (number of edges, number of colors,
  # vertex)
  def comp_vertex(self, a, b):
    val_a = a[0]
    if a[1] > 0:
      val_a = val_a / a[1]

    val_b = b[0]
    if b[1] > 0:
      val_b = val_b / b[1]

    if val_a < val_b:
      return 1
    elif val_a > val_b:
      return -1
    else:
      return 0

  # Returns the vertex with the maximum number of edges in A
  def get_max_vertex(self):
    count = []
    for v in self.V:
      num_edges = 0
      for p in self.A:
        a, b = p
        if a == v or b == v:
          num_edges += 1

      num_colors = 0
      if self.colors.has_key(v):
        if type(self.colors[v]) == int and self.colors[v] != -1:
          num_colors = 1
        elif type(self.colors[v]) == list:
          num_colors = len(self.colors[v])

      count.append((num_edges, num_colors, v))

    count.sort(self.comp_vertex)
    return count[0][2]

  # Used by PMNF to remove a vertex and all associated edges from V, A.
  def remove_vertex(self, v):
    i = 0
    while i < len(self.A):
      a, b = self.A[i]
      if a == v or b == v:
        self.A.pop(i)
      else:
        i += 1

    self.V.remove(v)

  def reset_va(self):
    self.V = self.V_orig[:]
    self.A = self.A_orig[:]

  def __init__(self, V, A):
    # List of vertices (nodes)
    self.V_orig = V[:]

    # List of adjacencies (links)
    self.A_orig = A[:]

    # Copy the vertex/adjacency lists so we can re-use them later
    self.reset_va()

    # Dictionary used to store edges for each vertex. Unlike V, A, this
    # dictionary is never changed. It will be used to determine distance-2
    # neighbors in subsequent steps.
    self.edges = {}

    # Dictionary to store assigned colors (integer values) for each vertex.
    # When running the initial UxDMA algorithm, the values will be integers.
    # Afterwares, these values will be converted to lists so additional colors
    # can be potentially assigned.
    self.colors = {}

    # The max color (slot number) we can use is MAXV
    MAXV = max(self.V)

    # Fill in the 'edges' dictionary
    for p in self.A[:]:
      a, b = p

      if not self.edges.has_key(a):
        self.edges[a] = []
      if not self.edges.has_key(b):
        self.edges[b] = []

      self.edges[a].append(b)
      self.edges[b].append(a)

    # Assign all vertices a color of -1 (invalid)
    for v in self.V:
      self.colors[v] = -1

    # Using PMNF ordering, greedily select a color for each vertex using the
    # distance-2 constraints. This loop will attempt to assign each vertex the
    # minimum color (integer) possible, however, we cannot use the same color
    # already used by vertices within the constrainted region.
    #
    # In each iteration of this loop, we will remove select the vertex with the
    # greatest number of edges. After processing this vertex, we will remove it
    # from V and A as defined by PMDF.
    while len(self.V) > 0:
      v = self.get_max_vertex()

      # Ignore vertices without edges
      if not self.edges.has_key(v):
        self.remove_vertex(v)
        continue

      used_colors = set()
      for e in self.edges[v]:
        # Check immediate neighbors
        if self.colors[e] >= 0:
          used_colors.add(self.colors[e])

    # Check two-hop neighbors (distance-2)
        for n in self.edges:
          if n == v:
            continue
          if self.colors[n] >= 0 and self.edges[n].count(e) > 0:
            used_colors.add(self.colors[n])

    # Assign the smallest colors value not being used within the constrained
    # region.
      for i in range(MAXV):
        if i not in used_colors:
          self.colors[v] = i
          break

    # With PMDF, we remove a vertex from consideration once it has been
    # assigned a color.
      self.remove_vertex(v)

    # Convert the color of each vertex to a list of colors.
    MAX_COLOR = max(self.colors.values())
    for k in self.colors:
      self.colors[k] = [self.colors[k]]

    # Attempt to add already assigned colors to each vertex to maximize color
    # (slot) allocations. Using the modified PMNF ordering, we try to give each
    # node slots they do not already have and are not being used by other
    # vertices in their constraint set.
    for i in range(MAX_COLOR):
      self.reset_va()

      while len(self.V) > 0:
        v = self.get_max_vertex()
        add_label = False

        # Ignore vertices without edges
        if not self.edges.has_key(v):
          self.remove_vertex(v)
          continue

    # Don't assign the same color twice
        if self.colors[v].count(i) > 0:
          self.remove_vertex(v)
          continue

        add_label = True
        for e in self.edges[v]:
          if self.colors[e].count(i) > 0:
            add_label = False
            break

          for n in self.edges:
            if n == v:
              continue
            if self.colors[n].count(i) > 0 and self.edges[n].count(e) > 0:
              add_label = False
              break

          if add_label is False:
            break

        if add_label:
          self.colors[v].append(i)

        self.remove_vertex(v)


def main():
  NODES = 10
  V = range(NODES)
  A = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (3, 6), (4, 6), (5, 6), (6, 7), (
      7, 8), (8, 9)]
  utdma = UXDMA_TDMA(V, A)
  print utdma.colors


if __name__ == "__main__":
  main()
