"""
DAA Assignment 5 – CO5: Search, Complexity and Approximation Engineering
All experiments are deterministic and use only the Python standard library.
"""
from itertools import combinations
from dataclasses import dataclass

# ---------------- B1: Instrumented graph colouring ----------------
@dataclass
class Stats:
    nodes: int = 0
    attempts: int = 0
    rejected: int = 0
    backtracks: int = 0
    max_depth: int = 0

def graph_colouring(vertices, edges, k, order="input"):
    adj={v:set() for v in vertices}
    for u,v in edges:
        adj[u].add(v); adj[v].add(u)
    sequence=list(vertices)
    colour={}
    st=Stats()
    def feasible(v,c):
        return all(colour.get(n)!=c for n in adj[v])
    def dfs(i):
        st.nodes += 1
        st.max_depth=max(st.max_depth,i)
        if i==len(vertices): return True
        if order=="degree":
            uncoloured=[x for x in vertices if x not in colour]
            # DSATUR: most distinct neighbour colours, then highest degree.
            v=max(uncoloured,key=lambda x:(len({colour[n] for n in adj[x] if n in colour}),len(adj[x]),-vertices.index(x)))
        else:
            v=next(x for x in sequence if x not in colour)
        for c in range(1,k+1):
            st.attempts += 1
            if not feasible(v,c):
                st.rejected += 1
                continue
            colour[v]=c
            if dfs(i+1): return True
            del colour[v]
            st.backtracks += 1
        return False
    ok=dfs(0)
    return ok, (dict(colour) if ok else None), st

def show_graph_result(label, vertices, edges, k):
    print(f"\n{label} | vertices={len(vertices)}, colours={k}, edges={len(edges)}")
    for mode in ("input","degree"):
        ok, col, s=graph_colouring(vertices,edges,k,mode)
        print(f"  {mode:6s}: colourable={ok}, colouring={col}, nodes={s.nodes}, "
              f"attempts={s.attempts}, rejected={s.rejected}, backtracks={s.backtracks}, "
              f"max_depth={s.max_depth}")

# ---------------- B3: Set cover exact and greedy ----------------
def set_cover_exact(universe, sets):
    """Enumerate centre subsets by increasing cardinality; count combinations checked."""
    centres=list(sets)
    checks=0
    for r in range(len(centres)+1):
        for chosen in combinations(centres,r):
            checks += 1
            covered=set()
            for c in chosen: covered |= set(sets[c])
            if set(universe) <= covered:
                return list(chosen), checks
    return None, checks

def set_cover_greedy(universe, sets):
    uncovered=set(universe); selected=[]; steps=0
    while uncovered:
        steps += 1
        best=None; best_gain=0
        for c,zones in sets.items():
            if c in selected: continue
            gain=len(uncovered & set(zones))
            if gain>best_gain:
                best_gain=gain; best=c
        if best is None: return None, steps
        selected.append(best)
        uncovered -= set(sets[best])
    return selected, steps

def show_cover(label, universe, sets):
    ex, checks=set_cover_exact(universe,sets)
    gr, steps=set_cover_greedy(universe,sets)
    print(f"{label}: zones={len(universe)}, centres={len(sets)}")
    print(f"  exact={ex} (size={len(ex) if ex is not None else None}, combinations_checked={checks})")
    print(f"  greedy={gr} (size={len(gr) if gr is not None else None}, greedy_rounds={steps})")

# ---------------- B4: First Fit Decreasing bin packing ----------------
def first_fit_decreasing(items, capacity):
    bins=[]
    for item in sorted(items, reverse=True):
        placed=False
        for b in bins:
            if sum(b)+item <= capacity:
                b.append(item); placed=True; break
        if not placed: bins.append([item])
    return bins

def main():
    print("DAA ASSIGNMENT 5 – EXECUTION RESULTS")
    print("====================================")
    # B1 validation cases
    show_graph_result("B1 Test 1: 5-cycle, 3 colours",
        [1,2,3,4,5], [(1,2),(2,3),(3,4),(4,5),(5,1)], 3)
    show_graph_result("B1 Test 2: triangle, 2 colours (impossible)",
        [1,2,3], [(1,2),(2,3),(1,3)], 2)
    show_graph_result("B1 Test 3: one isolated vertex",
        [1], [], 1)
    # B1 ordering comparison: graph with high-degree hub first heuristic
    show_graph_result("B1 Ordering comparison: hub-and-spokes plus rim",
        list("ABCDEF"), [( "A",x) for x in "BCDEF"]+[("B","C"),("C","D"),("D","E"),("E","F"),("F","B")], 3)
    # B2 same n and k; one easy, one difficult unsatisfiable graph
    show_graph_result("B2 Graph A: 8-vertex path, 2 colours",
        list(range(8)), [(i,i+1) for i in range(7)], 2)
    show_graph_result("B2 Graph B: 7-cycle plus isolated vertex, 2 colours",
        list(range(8)), [(i,(i+1)%7) for i in range(7)], 2)
    # B3 normal cases
    U1=set("ABCDEF"); S1={"C1":set("AB"),"C2":set("CD"),"C3":set("EF"),"C4":set("ACE"),"C5":set("BDF")}
    U2=set("12345"); S2={"C1":set("123"),"C2":set("45"),"C3":set("14"),"C4":set("235")}
    U3=set("WXYZ"); S3={"C1":set("WX"),"C2":set("YZ"),"C3":set("WY"),"C4":set("XZ")}
    print("\nB3 EXACT VS GREEDY SET COVER")
    show_cover("Instance 1",U1,S1); show_cover("Instance 2",U2,S2); show_cover("Instance 3",U3,S3)
    # Counterexample: greedy picks largest A (4 zones), then needs 2 more; optimum B+C
    U4=set("123456")
    S4={"A":set("1234"),"B":set("125"),"C":set("346")}
    print("\nB3 Counterexample (greedy not optimal)")
    show_cover("Counterexample",U4,S4)
    # Scale experiment: nested interval-like centres, exact checks combinations; greedy rounds
    print("\nB3 Scale evidence")
    for n in (8,10,12):
        U=set(range(n))
        sets={f"C{i}":set(range(i,min(i+4,n))) for i in range(0,n,2)}
        # add singleton coverage for guaranteed cover
        for j in range(n): sets[f"S{j}"]={j}
        ex,checks=set_cover_exact(U,sets); gr,steps=set_cover_greedy(U,sets)
        print(f"  zones={n}, centres={len(sets)}, exact_combinations_checked={checks}, "
              f"greedy_rounds={steps}, exact_size={len(ex)}, greedy_size={len(gr)}")
    # B4 Next Fit heuristic and challenging example
    print("\nB4 BIN PACKING – NEXT FIT")
    capacity=10; items=[7,6,5,5,4,3]
    bins=[]
    for item in items:
        if not bins or sum(bins[-1])+item>capacity: bins.append([item])
        else: bins[-1].append(item)
    print(f"  capacity={capacity}, workloads={items}")
    for i,b in enumerate(bins,1): print(f"  Server {i}: {b}, used={sum(b)}, remaining={capacity-sum(b)}")
    print(f"  servers_used={len(bins)}")
    # Explicit heuristic challenge: FFD uses 3 bins, optimum is 2 (10,10,10)
    challenge=[6,6,4,4,4,6]
    cbins=[]
    for item in challenge:
        if not cbins or sum(cbins[-1])+item>10: cbins.append([item])
        else: cbins[-1].append(item)
    print(f"\n  challenge workloads={challenge}, capacity=10")
    for i,b in enumerate(cbins,1): print(f"  Server {i}: {b}, remaining={10-sum(b)}")
    print(f"  NextFit_servers={len(cbins)}; feasible_optimum=3 (three 6+4 pairs)")

if __name__=="__main__": main()
