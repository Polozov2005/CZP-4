import pandapower as pp
import matplotlib.pyplot as plt
import pandas as pd

def network(Com1, Com2, Com3, Com4, Com5):
    """
    Создает модель электрической сети с заданными состояниями коммутационных аппаратов.
    """
    # Создаем пустую сеть
    net = pp.create_empty_network(f_hz=50.0, add_stdtypes=True)

    # Создаем шины (узлы)
    bus1 = pp.create_bus(net, vn_kv=110)
    bus2 = pp.create_bus(net, vn_kv=110)
    bus3 = pp.create_bus(net, vn_kv=10)
    bus4 = pp.create_bus(net, vn_kv=10)
    bus5 = pp.create_bus(net, vn_kv=10)

    bus14 = pp.create_bus(net, vn_kv=110)
    bus23 = pp.create_bus(net, vn_kv=110)

    # Создаем внешнюю энергосистему (слева от шины bus1)
    pp.create_ext_grid(net, bus=bus1, vm_pu=1.02, name="Grid Connection")

    # Создаем линии электропередачи
    line1 = pp.create_line_from_parameters(
        net, from_bus=bus1, to_bus=bus14, length_km=8.1,
        r_ohm_per_km=0.46, x_ohm_per_km=0.275, max_i_ka=0.265, c_nf_per_km=0
    )
    line2 = pp.create_line_from_parameters(
        net, from_bus=bus2, to_bus=bus23, length_km=9.3,
        r_ohm_per_km=0.46, x_ohm_per_km=0.275, max_i_ka=0.265, c_nf_per_km=0
    )
    line3 = pp.create_line_from_parameters(
        net, from_bus=bus1, to_bus=bus2, length_km=8.9,
        r_ohm_per_km=0.46, x_ohm_per_km=0.275, max_i_ka=0.265, c_nf_per_km=0
    )
    line4 = pp.create_line_from_parameters(
        net, from_bus=bus4, to_bus=bus5, length_km=1.3,
        r_ohm_per_km=0.12, x_ohm_per_km=0.378, max_i_ka=0.605, c_nf_per_km=0
    )
    line5 = pp.create_line_from_parameters(
        net, from_bus=bus3, to_bus=bus5, length_km=1.0,
        r_ohm_per_km=0.12, x_ohm_per_km=0.378, max_i_ka=0.605, c_nf_per_km=0
    )

    # Создаем трансформаторы
    trafo1 = pp.create_transformer_from_parameters(
        net, hv_bus=bus14, lv_bus=bus4, sn_mva=32, vn_hv_kv=110, vn_lv_kv=10,
        vk_percent=10.5, i0_percent=0.28, pfe_kw=160, vkr_percent=(160/320)
    )
    trafo2 = pp.create_transformer_from_parameters(
        net, hv_bus=bus23, lv_bus=bus3, sn_mva=32, vn_hv_kv=110, vn_lv_kv=10,
        vk_percent=10.5, i0_percent=0.28, pfe_kw=160, vkr_percent=(160/320)
    )

    # Создаем нагрузки
    load1 = pp.create_load(net, bus=bus2, p_mw=27, q_mvar=12)
    load2 = pp.create_load(net, bus=bus3, p_mw=5, q_mvar=3.1)
    load3 = pp.create_load(net, bus=bus4, p_mw=3, q_mvar=2.5)
    load4 = pp.create_load(net, bus=bus5, p_mw=4, q_mvar=3.3)

    # Создаем коммутационные аппараты (выключатели)
    Q1 = pp.create_switch(net, bus1, line3, et="l", closed=Com1)  # линия 3
    Q2 = pp.create_switch(net, bus1, line1, et="l", closed=Com2)  # линия 1
    Q3 = pp.create_switch(net, bus2, line2, et="l", closed=Com3)  # линия 2
    Q6 = pp.create_switch(net, bus3, line5, et="l", closed=Com4)  # линия 5
    Q7 = pp.create_switch(net, bus4, line4, et="l", closed=Com5)  # линия 4

    return net


def calculate_losses(P_line, Q_line, P_trafo, Q_trafo):
    """
    Рассчитывает суммарные потери мощности в сети.
    Потери в линиях и трансформаторах вычисляются по формуле: S = sqrt(P^2 + Q^2) * 0.5
    """
    S_line = (P_line**2 + Q_line**2)**0.5 * 0.5
    S_trafo = (P_trafo**2 + Q_trafo**2)**0.5 * 0.5
    S_sum = sum(S_line) + sum(S_trafo)
    return S_sum


# Базовый вариант: все линии включены
Com = [True, True, True, True, True]
Com1, Com2, Com3, Com4, Com5 = Com[0], Com[1], Com[2], Com[3], Com[4]
net_var0 = network(Com1, Com2, Com3, Com4, Com5)
pp.runpp(net_var0)

# Первый вариант: отключена линия 5 (соответствует Com4 = False)
Com = [True, True, True, False, True]
Com1, Com2, Com3, Com4, Com5 = Com[0], Com[1], Com[2], Com[3], Com[4]
net_var1 = network(Com1, Com2, Com3, Com4, Com5)
pp.runpp(net_var1)

# Второй вариант: отключена линия 4 (соответствует Com5 = False)
Com = [True, True, True, True, False]
Com1, Com2, Com3, Com4, Com5 = Com[0], Com[1], Com[2], Com[3], Com[4]
net_var2 = network(Com1, Com2, Com3, Com4, Com5)
pp.runpp(net_var2)

# Расчет и вывод суммарных потерь для всех вариантов
S_sum_var0 = calculate_losses(
    net_var0.res_line.p_from_mw, net_var0.res_line.q_from_mvar,
    net_var0.res_trafo.p_hv_mw, net_var0.res_trafo.q_hv_mvar
)
print('Суммарные потери при базовом варианте (все линии включены):')
print(S_sum_var0)

S_sum_var1 = calculate_losses(
    net_var1.res_line.p_from_mw, net_var1.res_line.q_from_mvar,
    net_var1.res_trafo.p_hv_mw, net_var1.res_trafo.q_hv_mvar
)
print('\nСуммарные потери при отключении линии 5:')
print(S_sum_var1)

S_sum_var2 = calculate_losses(
    net_var2.res_line.p_from_mw, net_var2.res_line.q_from_mvar,
    net_var2.res_trafo.p_hv_mw, net_var2.res_trafo.q_hv_mvar
)
print('\nСуммарные потери при отключении линии 4:')
print(S_sum_var2)