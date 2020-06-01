import numpy as np
from IPython.display import display, HTML

# Association of the values used in the data storage matrix
YES = 1
NO = 2
MAYBE = 0


class ZebraPuzzle:

    def __init__(self, categories_attributes: dict):
        self.categories_attributes: dict = categories_attributes
        # Prepare some convenience variables
        self.categories: list = list(self.categories_attributes.keys())
        self.number_categories: int = len(self.categories)
        self.number_attributes: int = len(self.categories_attributes[self.categories[0]])

        # Prepare some more convenience variables
        self.attributes = []
        for i, k in enumerate(self.categories):
            for j, n in enumerate(self.categories_attributes[k]):
                self.attributes.append(n.lower())
        self._tot: int = int(self.number_categories * self.number_attributes)

        # Check if each category has same number of attributes
        for k in self.categories_attributes:
            assert len(self.categories_attributes[k]) == self.number_attributes

        # Prepare the data-container
        self._data = np.zeros([self._tot, self._tot], dtype=int)
        # Initialize the trivial data
        assert YES == 1 and NO == 2, "If you want to change the values of YES and NO, please also change the code below accordingly."
        su = 2 * np.ones([self.number_attributes, ] * 2) - np.identity(self.number_attributes)
        for i in range(self.number_categories):
            self._data[i * self.number_attributes:(i + 1) * self.number_attributes,
            i * self.number_attributes:(i + 1) * self.number_attributes] = su

    def get_category(self, x: int) -> int:
        return int(x / self.number_attributes)

    def get_category_from_name(self, name: str) -> int:
        return self.get_category(self.get_id(name))

    def get_id(self, name: str) -> int:
        return self.attributes.index(name.lower())

    def get_assoc_name(self, a: str, b: str) -> int:
        return self.get_assoc(self.get_id(a), self.get_id(b))

    def get_assoc(self, a: int, b: int) -> int:
        assert a != b, "Requesting the association of a attribute with itself does not make sense."
        # assert that a and b are not from the same category
        assert self._data[a, b] == self._data[b, a]
        return self._data[min(a, b), max(a, b)]

    def add_assoc_name(self, name_a: str, name_b: str, assoc: bool):
        k_a = self.get_id(name_a)
        k_b = self.get_id(name_b)
        self.add_assoc(k_a, k_b, assoc)

    def add_assoc(self, a: int, b: int, assoc: bool):
        v = YES if assoc else NO
        assert self.get_assoc(a, b) == MAYBE or self.get_assoc(a, b) == v, \
            f"Try to overwrite field {a, b} with value {self.get_assoc(a, b)}."

        # In case of a positive assoc, we can already remove quite a few possibilities.
        if assoc:
            for i in range(self.number_attributes):
                self._data[self.get_category(a) * self.number_attributes + i, b] = NO
                self._data[a, self.get_category(b) * self.number_attributes + i] = NO
                self._data[b, self.get_category(a) * self.number_attributes + i] = NO
                self._data[self.get_category(b) * self.number_attributes + i, a] = NO

        self._data[a, b] = v
        self._data[b, a] = v

    def generate_matrix_html(self) -> str:
        from IPython.display import display, HTML
        # Some css to make the table look nice
        table = """
    <style type="text/css">
    table, th, td {
      border: 1px solid black;
      margin: 0px;
      padding: 0px;
    }
    th 
    {
      vertical-align: bottom;
      text-align: center;
    }
    
    th span 
    {
      -ms-writing-mode: tb-rl;
      -webkit-writing-mode: vertical-rl;
      writing-mode: vertical-rl;
      transform: rotate(180deg);
      white-space: nowrap;
      spacing: 2px;
    }
    </style>
    """
        # Now generate the required HTML
        table += '<table>'
        # Print categories
        table += '<tr><th></th><th></th>'
        for ki in range(1, self.number_categories):
            k = self.categories[ki]
            table += f"<th colspan='{self.number_attributes:d}' style='text-align:center;'>{k}</th><th></th>"
        table += "</tr><tr><th></th><th></th>"
        # Print attributes
        for ki in range(1, self.number_categories):
            k = self.categories[ki]
            for att in self.categories_attributes[k]:
                table += f"<th class='rotate'><span>{att}</span></th>"
            table += "<th></th>"
        table += "</tr><tr>"
        # Print main body
        for ki in range(0, self.number_categories - 1):
            # Print categories on left
            k = self.categories[ki]
            table += f"<th rowspan='{self.number_attributes:d}'><span>{k}</span></th>"
            for i, att in enumerate(self.categories_attributes[k]):
                # Print attributes on left
                it = ki * self.number_attributes + i
                table += f"<th>{att}</th>"
                for kj in range(1, self.number_categories):
                    for j, att2 in enumerate(self.categories_attributes[k]):
                        # Print values
                        jt = kj * self.number_attributes + j
                        if kj <= ki:
                            c = "-"
                        elif self.get_assoc(jt, it) == YES:
                            c = 'o'
                        elif self.get_assoc(jt, it) == NO:
                            c = 'x'
                        else:
                            c = '.'
                        table += f"<td>{c}</td>"
                    table += f"<td>|</td>"
                table += "</tr><tr>"
            table += "<td>-</td>" * (2 + (self.number_categories - 1) * (self.number_attributes + 1))
            table += "</tr><tr>"
        table += '</tr></table>'
        table += f"Filled about {int(np.round(self.get_percentage_solved())):d}% of the puzzle."
        return table

    def display_matrix(self):
        # Display output
        html_table = HTML(self.generate_matrix_html())
        display(html_table)

    def _exclude(self, x: int, y: int):
        assert self.get_assoc(x, y) == YES
        kx = self.get_category(x)
        ky = self.get_category(y)
        for xi in range(0, self._tot):
            if xi != y and self.get_assoc(xi, y) == NO:
                if self.get_category(xi) != kx and self.get_category(xi) != ky:
                    if self.get_assoc(x, xi) == MAYBE:
                        print(f"By simple logic '{self.attributes[x]}' and '{self.attributes[xi]}'" +
                              f" are negatively associated.")
                        self.add_assoc(x, xi, False)

    def exclude_all(self):
        for i in range(self._tot):
            for j in range(i + 1, self._tot):
                if self.get_assoc(i, j) == YES:
                    self._exclude(i, j)
                    self._exclude(j, i)

    def find_solved(self):
        for ki in range(self.number_categories):
            for kj in range(ki + 1, self.number_categories):
                sr, er = ki * self.number_attributes, (ki + 1) * self.number_attributes
                for x in range(sr, er):
                    sc, ec = kj * self.number_attributes, (kj + 1) * self.number_attributes
                    d = [r == NO for r in self._data[x, sc:ec]]
                    # print(x, f"{sc}:{ec}", d)
                    if sum(d) == self.number_attributes - 1:
                        for y in range(sc, ec):
                            if self.get_assoc(x, y) == 0:
                                print(f"By simple logic '{self.attributes[x]}' and '{self.attributes[y]}'" +
                                      f" are positively associated.")
                                # print(self._data[x, sc:ec])
                                self.add_assoc(x, y, True)
                # Other way around.
                # TODO: this is ugly code-duplication. Re-implement this at your leisure.
                sc, ec = kj * self.number_attributes, (kj + 1) * self.number_attributes
                for y in range(sc, ec):
                    d = [r == NO for r in self._data[sr:er, y]]
                    # print(x, f"{sc}:{ec}", d)
                    if sum(d) == self.number_attributes - 1:
                        for x in range(sr, er):
                            if self._data[x, y] == 0:
                                print(f"By simple logic '{self.attributes[x]}' and '{self.attributes[y]}'" +
                                      f" are positively associated.")
                                # print(self._data[sc:ec, y])
                                self.add_assoc(x, y, True)

    def iterate_logic(self):
        p = 0
        while self.get_percentage_solved() > p:
            p = self.get_percentage_solved()
            self.exclude_all()
            self.find_solved()

    def get_percentage_solved(self):
        # Estimates the percentage to which this puzzle is solved.
        n = self._tot
        m = self.number_attributes
        n_yes = self.number_categories ** 2 * m
        init = self.number_categories * (m ** 2 - m) * NO + self.number_categories * m * YES

        return 100 * (np.sum(self._data) - init) / (YES * n_yes + NO * (n ** 2 - n_yes) - init)
