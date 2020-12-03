import codes
jobs = ["마피아", "마피아", "시민", "시민", "시민", "군인", "의사", "경찰"]  # 직업 배열
jobs_num = codes.jobs_random()


class User:

    def __init__(self, name, life):
        self.name = name
        self.life = life
