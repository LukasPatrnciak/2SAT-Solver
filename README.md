# 2-SAT Solver: Static and Dynamic

Projekt implementuje riešenie problému **2-splniteľnosti (2-SAT)** v dvoch režimoch:

1. **Statický batch solver** – načíta celú formulu naraz a rozhodne, či je splniteľná.
2. **Dynamický interaktívny solver** – postupne prijíma klauzuly, udržiava aktuálny stav ako SAT a pri nesplniteľnej klauzule vykoná rollback.

## Odporúčaný názov zadania

**Statický a dynamický 2-SAT solver**

Alternatívne názvy:

- **Incremental 2-SAT Solver**
- **2-SAT Solver s rollbackom**
- **SAT/UNSAT detektor pomocou implikačného grafu**

## Myšlienka riešenia

Každá klauzula tvaru:

```text
(a ∨ b)
```

sa prevedie na dve implikácie:

```text
¬a → b
¬b → a
```

Následne sa vytvorí **implikačný graf**.

Formula je **UNSAT**, ak pre niektorú premennú `x` platí, že `x` a `¬x` sú v tej istej silne súvislej komponente.

Teda:

```text
component[x] == component[¬x]
```

Ak to nenastane, formula je **SAT**.

## Použitý algoritmus

Na statické overenie splniteľnosti je použitý **Tarjanov algoritmus** na hľadanie silne súvislých komponentov.

Časová zložitosť statického solvera:

```text
O(N + M)
```

kde:

- `N` je počet premenných,
- `M` je počet klauzúl.

## Režimy programu

Program podporuje dva režimy:

```bash
python two_sat_solver.py static
```

alebo:

```bash
python two_sat_solver.py dynamic
```

Ak sa režim nezadá, predvolený je interaktívny režim:

```bash
python two_sat_solver.py
```

## Statický režim 

### Vstup

Prvý riadok obsahuje:

```text
N M
```

kde:

- `N` je počet premenných,
- `M` je počet klauzúl.

Nasleduje `M` riadkov, každý obsahuje dvojicu literálov:

```text
l1 l2
```

Kladné číslo znamená premennú `x`, záporné číslo znamená negáciu `¬x`.

### Príklad vstupu

```text
2 2
1 2
-1 2
```

To znamená:

```text
(x1 ∨ x2)
(¬x1 ∨ x2)
```

### Spustenie

```bash
python two_sat_solver.py static < input.txt
```

### Výstup

Ak je formula splniteľná:

```text
SAT
x1 = 0
x2 = 1
```

Ak je formula nesplniteľná:

```text
UNSAT
Critical conflict: x1 and -x1 are in the same SCC
```

## Dynamický režim

V dynamickom režime sa príkazy zadávajú postupne.

### Podporované príkazy

#### Pridanie klauzuly

```text
A l1 l2
```

Pridá klauzulu:

```text
(l1 ∨ l2)
```

Napríklad:

```text
A 1 2
```

znamená:

```text
(x1 ∨ x2)
```

#### Výpis aktuálneho priradenia

```text
S
```

Vypíše aktuálne platné SAT priradenie.

#### Ukončenie programu

```text
Q
```

Ukončí program.

## Rollback

Ak operácia `A l1 l2` spôsobí nesplniteľnosť, program:

1. zamietne klauzulu,
2. odstráni práve pridané hrany,
3. ponechá systém v pôvodnom SAT stave.

Teda neúspešná operácia nezanechá v grafe žiadne nové hrany.

## Príklad dynamického behu

### Vstup

```text
A 1 2
A -1 2
S
A -2 -2
S
Q
```

### Výstup

```text
ADDED: (1 v 2)
ADDED: (-1 v 2)
SAT
x1 = 0
x2 = 1
UNSAT: Clause (-2 v -2) rejected.
Path detected: 2 -> -2
SAT
x1 = 0
x2 = 1
```

## Súbory

```text
two_sat_solver.py   hlavná implementácia
README.md           dokumentácia projektu
```

## Poznámka

Dynamická časť v tejto implementácii používa po každom pridaní klauzuly Tarjanov algoritmus na kontrolu SAT/UNSAT. Je to jednoduché, prehľadné a vhodné ako základná implementácia. Pre plne optimalizovanú verziu by sa dala doplniť inkrementálna kontrola dosiahnuteľnosti iba v dotknutej časti grafu.
