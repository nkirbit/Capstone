import numpy as np

def generate_result_string(model, state, business, state_pop, state_df):
    hypotheses = '(lag(x, 1, num_states) = lag(x, 2, num_states) = lag(x, 3, num_states) = lag(x, 4, num_states) = 0)'
    f_test = model.f_test(hypotheses)
    p_value = f_test.pvalue[()]
    coefs = model.params[1:5]
    latest_covid_100k = np.round((state_df.transpose().diff(1).values[-1][0] / state_pop ) * 100000,2)
    sum_change = np.sum(coefs.values)
    sum_change_times_10 = np.round(sum_change * 10,2)
    if p_value > 0.1:
        string1 = f"COVID-19 does not have a significant impact on consumer's \
                    interest in {business}"
        string2 = "Not influenced by COVID-19"
    elif p_value > 0.007:
        if sum_change > 0:
            string1 = f"An increase in COVID-19 cases leads to a moderate increase in \
            consumer interest in {business}. If cases increase by 10 per 100k people, \
            consumer interest would increase by {sum_change_times_10}%. For reference, \
            the case rate in {state} is currently {latest_covid_100k} per 100k people"
            string2 = "Somewhat positively influenced by COVID-19"
        else:
            string1 = f"An increase in COVID-19 cases leads to a moderate decrease in \
            consumer interest in {business}. If cases increase by 10 per 100k people, \
            consumer interest would decrease by {-1 * sum_change_times_10}%. For reference, \
            the case rate in {state} is currently {latest_covid_100k} per 100k people"
            string2 = "Somewhat negatively influenced by COVID-19"
    else:
        if sum_change > 0:
            string1 = f"An increase in COVID-19 cases leads to a large increase in \
            consumer interest in {business}. If cases increase by 10 per 100k people, \
            consumer interest would increase by {sum_change_times_10}%. For reference, \
            the case rate in {state} is currently {latest_covid_100k} per 100k people"
            string2 = "Greatly positively influenced by COVID-19"
        else:
            string1 = f"An increase in COVID-19 cases leads to a large decrease in \
            consumer interest in {business}. If cases increase by 10 per 100k people, \
            consumer interest would decrease by {-1 * sum_change_times_10}%. For reference, \
            the case rate in {state} is currently {latest_covid_100k} per 100k people"
            string2 = "Greatly negatively influenced by COVID-19"
    return string1, string2
