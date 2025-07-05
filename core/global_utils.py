def mes_selecionado(meses_var, mes_atual, var_atual):
    if var_atual.get():
        for mes, var in meses_var:
            if mes != mes_atual:
                var.set(False)
