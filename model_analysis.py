def do_some_analysis(model,state,business):
    hypothesis = '(lag(x, 1, num_states) = lag(x, 2, num_states) = \
    lag(x, 3, num_states) = lag(x, 4, num_states) = 0)'
    f_test = model.f_test(hypothesis)
    f_p_value = f_test.pvalue[()]
    coefs = model.params[1:5]
    if f_p_value > 0.1:
        output_string = f'COVID-19 rates do not influence consumer interest in {business}.'
    else:
        output_string = f'COVID-19 has influence on {business}.'
    pvalues = model.pvalues[1:5]
    tvalues = model.tvalues[1:5]
    stderrors = model.bse[1:5]
    table_values = [coefs,stderrors,tvalues,pvalues]
    return table_values, f_p_value, output_string
