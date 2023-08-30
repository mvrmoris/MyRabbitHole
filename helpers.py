def astrology_sign(name):
    signs = [None,'aries','taurus','gemini','cancer','leo','virgo','libra','scorpio','sagittarius','capricorn','acquarius','pisces']
    symbols = ['','♈︎','♉︎','♊︎','♋︎','♌︎','♍︎','♎︎','♏︎','♐︎','♑︎','♒︎','♓︎']
    for i in range(len(signs)):
        if signs[i] == name:
            return(symbols[i])
def mbti_type(mbti):
    mbti_type = {None: '',"architect": "INTJ", "logician":"INTP","commander":"ENTJ","debater" : "ENTP","advocate": "INFJ","mediator":"INFP","protagonist": "ENFJ","compaigner":"ENFP","logistician":"ISTJ","defender":"ISFJ","executive":"ESTJ","consul": "ESFJ", "virtuoso":"ISTP","adventurer":"ISFP","entrepeneur":"ESTP","entertainer":"ESFP"}
    return(mbti_type[mbti])
