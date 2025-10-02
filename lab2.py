from collections import deque, defaultdict

class KnowledgeBase:
    def __init__(self):
        # Орієнтований граф: вузол -> список (тип_відношення, інший_вузол)
        self.relations = defaultdict(list)

        self.relation_types = [
            "is_a", "part_of", "located_in",
            "teaches", "studies", "offers",
            "enrolled_in", "requires"
        ]


    def add_relation(self, subj, relation, obj):
        self.relations[subj].append((relation, obj))
        _ = self.relations[obj]  # гарантуємо ключ

    # -------- (“спеціальні команди”) --------
    def list_relations(self, obj):
        """Вивести всі вихідні відношення для об'єкта."""
        if obj not in self.relations:
            print(f"{obj} not found in KB")
            return
        print(f"Relations for {obj}:")
        if not self.relations[obj]:
            print("  (none)")
            return
        for rel, target in self.relations[obj]:
            print(f"  {obj} -[{rel}]-> {target}")

    def list_by_type(self, relation_type):
        """Вивести всі зв’язки конкретного типу."""
        print(f"All relations of type '{relation_type}':")
        found = False
        for subj, rels in self.relations.items():
            for rtype, obj in rels:
                if rtype == relation_type:
                    found = True
                    print(f"  {subj} -[{rtype}]-> {obj}")
        if not found:
            print("  (none)")

    def list_all_objects(self):
        """Список усіх відомих вузлів (субʼєкти та обʼєкти)."""
        objs = sorted(self.relations.keys())
        print(f"Total objects: {len(objs)}")
        for o in objs:
            print(f"  - {o}")

    def list_relation_types(self):
        """Довідник доступних типів відношень."""
        print("Relation types:")
        for t in self.relation_types:
            print(f"  - {t}")

    def neighbors(self, obj, relation_type=None):
        """Безпосередні сусіди обʼєкта (фільтр за типом, якщо задано)."""
        if obj not in self.relations:
            print(f"{obj} not found in KB")
            return
        if relation_type is None:
            print(f"Neighbors of {obj} (any relation):")
            outs = self.relations[obj]
        else:
            print(f"Neighbors of {obj} by relation '{relation_type}':")
            outs = [(r, o) for (r, o) in self.relations[obj] if r == relation_type]
        if not outs:
            print("  (none)")
            return
        for r, o in outs:
            print(f"  -[{r}]-> {o}")

    # -------- QUERIES --------
    # Пошук по одному типу
    def _query_type(self, start, end, relation_type):
        visited = set()
        stack = [start]
        while stack:
            node = stack.pop()
            if node == end:
                return True
            if node in visited:
                continue
            visited.add(node)
            for rtype, nxt in self.relations[node]:
                if rtype == relation_type and nxt not in visited:
                    stack.append(nxt)
        return False

    def query_type(self, start, end, relation_type):
        return self._query_type(start, end, relation_type)

    # Пошук по будь-яких типах — BFS з відновленням шляху
    def query_any_with_path(self, start, end):
        if start not in self.relations or end not in self.relations:
            return False, ""

        visited = set([start])
        q = deque([start])
        parents = {start: (None, None)}

        while q:
            node = q.popleft()
            if node == end:

                return True, self._reconstruct_path(parents, start, end)
            for rtype, nxt in self.relations[node]:
                if nxt not in visited:
                    visited.add(nxt)
                    parents[nxt] = (node, rtype)
                    q.append(nxt)

        return False, ""

    def _reconstruct_path(self, parents, start, end):
        # повертає строку виду: A -[r]-> B -[r]-> C
        chain = []
        cur = end
        while cur is not None:
            prev, rtype = parents[cur]
            chain.append((prev, rtype, cur))
            cur = prev
        chain.reverse()
        pretty = []
        for prev, rtype, cur in chain:
            if prev is None:
                pretty.append(cur)
            else:
                pretty.append(f"-[{rtype}]-> {cur}")
        return " ".join(pretty)

    def check(self, obj1, obj2, mode="any", echo=True):
        """Перевірка звʼязку.
        mode="any" — змішані шляхи; або конкретний тип: "is_a" / "part_of" / ...
        """
        if obj1 not in self.relations or obj2 not in self.relations:
            if echo:
                print("Objects not found!")
            return False

        if mode == "any":
            ok, path = self.query_any_with_path(obj1, obj2)
            if ok:
                if echo:
                    print("Yes")
                    print(f"Path: {path}")
                return True

            okr, pathr = self.query_any_with_path(obj2, obj1)
            if okr:
                if echo:
                    print("Yes (reverse)")
                    print(f"Path: {pathr}")
                return True
            if echo:
                print("No")
            return False
        else:

            if self.query_type(obj1, obj2, mode) or self.query_type(obj2, obj1, mode):
                if echo:
                    print("Yes")
                return True
            if echo:
                print("No")
            return False

    def shortest_path(self, obj1, obj2):
        """Повернути лише шлях (рядок), якщо він існує, інакше пусто."""
        ok, path = self.query_any_with_path(obj1, obj2)
        if ok:
            return path
        okr, pathr = self.query_any_with_path(obj2, obj1)
        if okr:
            return f"(reverse) {pathr}"
        return ""




kb = KnowledgeBase()

# --- IS_A ---
kb.add_relation("Entity", "is_a", "Thing")
kb.add_relation("Organization", "is_a", "Entity")
kb.add_relation("Educational_Organization", "is_a", "Organization")
kb.add_relation("Institution", "is_a", "Educational_Organization")
kb.add_relation("University", "is_a", "Institution")
kb.add_relation("College", "is_a", "Institution")

kb.add_relation("Organizational_Unit", "is_a", "Entity")
kb.add_relation("Academic_Unit", "is_a", "Entity")
kb.add_relation("Activity", "is_a", "Entity")
kb.add_relation("Assessment", "is_a", "Entity")
kb.add_relation("Person", "is_a", "Entity")
kb.add_relation("Facility", "is_a", "Entity")
kb.add_relation("Resource", "is_a", "Entity")
kb.add_relation("Place", "is_a", "Entity")

kb.add_relation("Faculty", "is_a", "Organizational_Unit")
kb.add_relation("Department", "is_a", "Organizational_Unit")
kb.add_relation("Program", "is_a", "Academic_Unit")
kb.add_relation("Course", "is_a", "Academic_Unit")
kb.add_relation("Discipline", "is_a", "Academic_Unit")

kb.add_relation("Lecture", "is_a", "Activity")
kb.add_relation("Lab", "is_a", "Activity")
kb.add_relation("Exam", "is_a", "Assessment")
kb.add_relation("Credit", "is_a", "Assessment")

kb.add_relation("University_Staff", "is_a", "Person")
kb.add_relation("Teacher", "is_a", "University_Staff")
kb.add_relation("Librarian", "is_a", "University_Staff")
kb.add_relation("Student", "is_a", "Person")

kb.add_relation("Book", "is_a", "Resource")
kb.add_relation("Online_Course", "is_a", "Resource")

kb.add_relation("Room", "is_a", "Facility")
kb.add_relation("Classroom", "is_a", "Room")
kb.add_relation("Laboratory", "is_a", "Room")
kb.add_relation("Library", "is_a", "Facility")

kb.add_relation("Campus", "is_a", "Place")
kb.add_relation("Building", "is_a", "Place")
kb.add_relation("City", "is_a", "Place")
kb.add_relation("Country", "is_a", "Place")

# --- PART_OF ---
kb.add_relation("Faculty", "part_of", "University")
kb.add_relation("Department", "part_of", "Faculty")
kb.add_relation("Program", "part_of", "Department")
kb.add_relation("Course", "part_of", "Program")
kb.add_relation("Discipline", "part_of", "Course")

kb.add_relation("Classroom", "part_of", "Building")
kb.add_relation("Laboratory", "part_of", "Building")
kb.add_relation("Library", "part_of", "Building")
kb.add_relation("Building", "part_of", "Campus")

# --- LOCATED_IN ---
kb.add_relation("Campus", "located_in", "City")
kb.add_relation("City", "located_in", "Country")


universities = ["KNU_Shevchenko", "Harvard_University"]
for u in universities:
    kb.add_relation(u, "is_a", "University")

faculties = ["Faculty_Cybernetics", "Faculty_Economics", "Faculty_Math", "Faculty_Engineering"]
for f in faculties:
    kb.add_relation(f, "is_a", "Faculty")

departments = ["Dept_AI", "Dept_Econometrics", "Dept_Algebra", "Dept_Software_Eng"]
for d in departments:
    kb.add_relation(d, "is_a", "Department")

programs = ["Program_CS_BSc", "Program_CS_MSc", "Program_Econ_BSc", "Program_SE_BSc"]
for p in programs:
    kb.add_relation(p, "is_a", "Program")

courses = ["Course_Programming", "Course_Algorithms", "Course_Microeconomics", "Course_DB_Systems"]
for c in courses:
    kb.add_relation(c, "is_a", "Course")

disciplines = ["Python_Programming", "Data_Structures", "Microeconomics_1", "Microeconomics_2", "Relational_Databases"]
for d in disciplines:
    kb.add_relation(d, "is_a", "Discipline")

teachers = ["Prof_Ivanenko", "Prof_Smith", "Dr_Petrova"]
for t in teachers:
    kb.add_relation(t, "is_a", "Teacher")

students = ["Student_Andrii", "Student_Maria", "Student_Oleh"]
for s in students:
    kb.add_relation(s, "is_a", "Student")

books = ["Book_CLRS", "Book_Mankiw", "Book_DB_Design"]
for b in books:
    kb.add_relation(b, "is_a", "Book")

rooms = ["Classroom_A101", "Lab_AI_201", "Library_Main"]
kb.add_relation("Classroom_A101", "is_a", "Classroom")
kb.add_relation("Lab_AI_201", "is_a", "Laboratory")
kb.add_relation("Library_Main", "is_a", "Library")

campuses = ["Campus_Kyiv", "Campus_Cambridge"]
for c in campuses:
    kb.add_relation(c, "is_a", "Campus")
buildings = ["Building_A", "Building_B", "Building_Widener"]
for b in buildings:
    kb.add_relation(b, "is_a", "Building")

cities = ["Kyiv", "Cambridge_MA"]
countries = ["Ukraine", "USA"]
for city in cities:
    kb.add_relation(city, "is_a", "City")
for country in countries:
    kb.add_relation(country, "is_a", "Country")


kb.add_relation("Faculty_Cybernetics", "part_of", "KNU_Shevchenko")
kb.add_relation("Faculty_Economics", "part_of", "KNU_Shevchenko")
kb.add_relation("Faculty_Math", "part_of", "Harvard_University")
kb.add_relation("Faculty_Engineering", "part_of", "Harvard_University")

kb.add_relation("Dept_AI", "part_of", "Faculty_Cybernetics")
kb.add_relation("Dept_Software_Eng", "part_of", "Faculty_Cybernetics")
kb.add_relation("Dept_Econometrics", "part_of", "Faculty_Economics")
kb.add_relation("Dept_Algebra", "part_of", "Faculty_Math")

kb.add_relation("Program_CS_BSc", "part_of", "Dept_AI")
kb.add_relation("Program_CS_MSc", "part_of", "Dept_AI")
kb.add_relation("Program_SE_BSc", "part_of", "Dept_Software_Eng")
kb.add_relation("Program_Econ_BSc", "part_of", "Dept_Econometrics")

kb.add_relation("Course_Programming", "part_of", "Program_CS_BSc")
kb.add_relation("Course_Algorithms", "part_of", "Program_CS_BSc")
kb.add_relation("Course_DB_Systems", "part_of", "Program_SE_BSc")
kb.add_relation("Course_Microeconomics", "part_of", "Program_Econ_BSc")

kb.add_relation("Python_Programming", "part_of", "Course_Programming")
kb.add_relation("Data_Structures", "part_of", "Course_Algorithms")
kb.add_relation("Relational_Databases", "part_of", "Course_DB_Systems")
kb.add_relation("Microeconomics_1", "part_of", "Course_Microeconomics")
kb.add_relation("Microeconomics_2", "part_of", "Course_Microeconomics")

# Розміщення
kb.add_relation("Campus_Kyiv", "located_in", "Kyiv")
kb.add_relation("Kyiv", "located_in", "Ukraine")
kb.add_relation("Campus_Cambridge", "located_in", "Cambridge_MA")
kb.add_relation("Cambridge_MA", "located_in", "USA")

kb.add_relation("Building_A", "part_of", "Campus_Kyiv")
kb.add_relation("Building_B", "part_of", "Campus_Kyiv")
kb.add_relation("Building_Widener", "part_of", "Campus_Cambridge")
kb.add_relation("Classroom_A101", "part_of", "Building_A")
kb.add_relation("Lab_AI_201", "part_of", "Building_A")
kb.add_relation("Library_Main", "part_of", "Building_B")

# Академічні відношення
kb.add_relation("Dept_AI", "offers", "Program_CS_BSc")
kb.add_relation("Dept_Software_Eng", "offers", "Program_SE_BSc")
kb.add_relation("Dept_Econometrics", "offers", "Program_Econ_BSc")

kb.add_relation("Program_CS_BSc", "offers", "Course_Programming")
kb.add_relation("Program_CS_BSc", "offers", "Course_Algorithms")
kb.add_relation("Program_SE_BSc", "offers", "Course_DB_Systems")
kb.add_relation("Program_Econ_BSc", "offers", "Course_Microeconomics")

kb.add_relation("Course_Programming", "requires", "Python_Programming")
kb.add_relation("Course_Algorithms", "requires", "Data_Structures")
kb.add_relation("Course_DB_Systems", "requires", "Relational_Databases")
kb.add_relation("Course_Microeconomics", "requires", "Microeconomics_1")

kb.add_relation("Prof_Ivanenko", "teaches", "Python_Programming")
kb.add_relation("Prof_Smith", "teaches", "Microeconomics_1")
kb.add_relation("Dr_Petrova", "teaches", "Relational_Databases")

kb.add_relation("Student_Andrii", "studies", "Python_Programming")
kb.add_relation("Student_Andrii", "enrolled_in", "Program_CS_BSc")
kb.add_relation("Student_Maria", "studies", "Microeconomics_1")
kb.add_relation("Student_Maria", "enrolled_in", "Program_Econ_BSc")
kb.add_relation("Student_Oleh", "studies", "Relational_Databases")
kb.add_relation("Student_Oleh", "enrolled_in", "Program_SE_BSc")

kb.add_relation("Book_CLRS", "part_of", "Data_Structures")
kb.add_relation("Book_Mankiw", "part_of", "Microeconomics_1")
kb.add_relation("Book_DB_Design", "part_of", "Relational_Databases")

kb.add_relation("KNU_Shevchenko", "located_in", "Campus_Kyiv")
kb.add_relation("Harvard_University", "located_in", "Campus_Cambridge")


HELP = """
Commands:
  check A B                - чи є звʼязок між A і B (будь-які типи, з виводом шляху)
  checktype A B TYPE       - чи є звʼязок ТИПУ (is_a/part_of/...) між A і B (без змішування)
  path A B                 - вивести найкоротший шлях (будь-які типи), або (reverse) шлях
  rel A                    - показати всі відношення, що виходять з A
  type T                   - показати всі відношення типу T
  neighbors A [TYPE]       - безпосередні сусіди вузла A (за типом або всі)
  objects                  - показати всі відомі обʼєкти
  types                    - показати всі зареєстровані типи відношень
  help                     - показати цю довідку
  exit                     - вийти
"""

print("KB ready. Type 'help' for commands.")
while True:
    try:
        line = input("> ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nBye!")
        break
    if not line:
        continue
    parts = line.split()
    cmd = parts[0].lower()

    if cmd == "exit":
        print("Bye!")
        break
    elif cmd == "help":
        print(HELP)
    elif cmd == "check" and len(parts) >= 3:
        _, a, b = parts[:3]
        kb.check(a, b, mode="any")
    elif cmd == "checktype" and len(parts) >= 4:
        _, a, b, t = parts[:4]
        kb.check(a, b, mode=t)
    elif cmd == "path" and len(parts) >= 3:
        _, a, b = parts[:3]
        path = kb.shortest_path(a, b)
        if path:
            print("Path:", path)
        else:
            print("No path")
    elif cmd == "rel" and len(parts) >= 2:
        _, a = parts[:2]
        kb.list_relations(a)
    elif cmd == "type" and len(parts) >= 2:
        _, t = parts[:2]
        kb.list_by_type(t)
    elif cmd == "neighbors" and len(parts) >= 2:
        if len(parts) == 2:
            _, a = parts
            kb.neighbors(a, relation_type=None)
        else:
            _, a, t = parts[:3]
            kb.neighbors(a, relation_type=t)
    elif cmd == "objects":
        kb.list_all_objects()
    elif cmd == "types":
        kb.list_relation_types()
    else:
        print("Unknown or malformed command. Type 'help' for usage.")
