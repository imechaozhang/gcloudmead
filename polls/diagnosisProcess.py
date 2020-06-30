import pandas as pd


class DiagnoseProcess:
    filename = 'polls/templates/polls/wm.csv'
    weight_matrix = pd.read_csv(filename, index_col=0)

    def __init__(self):
        self.wm = self.weight_matrix.copy(deep=True)
        self.asked = []
        self.positive = []
        self.age = 'Adults'
        self.gender = 'Male'
        # self.map = {'Male': 28, 'Female': 29, 'Children': 30, 'Adults': 31, 'Elderly': 32}
        self.diagnosis = ''

    def reduce(self):
        self.wm = self.weight_matrix.copy(deep=True)
        for symptom in self.asked:
            if symptom in self.positive:
                self.wm = self.wm[self.wm[symptom] > 0]
            else:
                self.wm = self.wm[self.wm[symptom] <= 0]
        for symptom in self.asked:
            if symptom in self.wm.columns:
                self.wm.drop(columns=symptom, inplace=True)
        for symptom in self.weight_matrix.columns[28:]:
            if symptom in self.wm.columns:
                self.wm.drop(columns=symptom, inplace=True)

    def time_to_conclude(self):
        return len(self.wm) <= 1

    def next_symptom(self):
        next_symp = self.wm.columns[0]
        max_priority = len(self.weight_matrix)
        for symp in self.wm.columns:
            value_counts = {'0': 0, '1': 0}
            for dis in self.wm[symp].values:
                if dis > 0:
                    value_counts['1'] += 1
                else:
                    value_counts['0'] += 1
            priority = abs(value_counts['1'] - value_counts['0'])
            if priority < max_priority:
                max_priority = priority
                next_symp = symp
        return next_symp

    def check(self):
        symptom_list = pd.Series(index=self.weight_matrix.columns, data=[0] * len(self.weight_matrix.columns))
        for symp in self.positive:
            symptom_list[symp] = 1

        symptom_list[self.gender] = 1
        symptom_list[self.age] = 1

        diagnosis_result = self.weight_matrix.dot(symptom_list)
        s = sum(diagnosis_result)
        for key in diagnosis_result.index:
            if diagnosis_result.loc[key] == 0:
                diagnosis_result.drop(key, inplace=True)
            else:
                diagnosis_result.loc[key] = round(diagnosis_result.loc[key] / s, 2)

        diagnosis_result.sort_values(ascending=False, inplace=True)
        self.diagnosis = diagnosis_result.keys()[0]
        return diagnosis_result

    def recommendation(self):
        drugs = pd.read_csv('polls/templates/polls/drugrec.csv', index_col=0)
        labs = pd.read_csv('polls/templates/polls/labrec.csv', index_col=0)
        drug = []
        lab = []
        if self.diagnosis in drugs.index:
            for c in drugs.columns:
                if str(drugs.loc[self.diagnosis, c]) != 'nan':
                    drug.append(str(drugs.loc[self.diagnosis, c]).strip())
        if self.diagnosis in labs.index:
            for c in labs.columns:
                if str(labs.loc[self.diagnosis, c]) != 'nan':
                    lab.append(str(labs.loc[self.diagnosis, c]).strip())
        if not drug:
            drug_str = "No drug recommendations found"
        else:
            drug_str = ', '.join(drug)
        if not lab:
            lab_str = "No lab test recommendations found"
        else:
            lab_str = ', '.join(lab)

        recommend = [str(drug_str), str(lab_str)]
        return recommend


class Question:
    def __init__(self, question_text):
        self.id = 0
        self.question_text = question_text
        self.choices = []
        c = {1: 'Severe', 2: 'Moderate', 3: 'light', 4: 'No'}

        for k, v in c.items():
            self.choices.append(Choice(choice_id=k, choice_text=v))


class Choice:
    def __init__(self, choice_id, choice_text):
        self.id = choice_id
        self.choice_text = choice_text
