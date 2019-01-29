# import sys
# sys.path.insert(0, '../../src/scenarios')
# from mdl_txop import MDLTxOp
#
# class ScheduleModifierTestData:
#     txop_timeout = 255
#     center_frequency_hz = 4919500000
#     txop1 = TxOp(StartUSec=0, StopUSec=11500, TxOpTimeout=txop_timeout, CenterFrequencyHz=center_frequency_hz, link_direction='up')
#     txop2 = TxOp(StartUSec=12500, StopUSec=24000, TxOpTimeout=txop_timeout, CenterFrequencyHz=center_frequency_hz, link_direction='down')
#     txop3 = TxOp(StartUSec=25000, StopUSec=48000, TxOpTimeout=txop_timeout, CenterFrequencyHz=center_frequency_hz, link_direction='up')
#     txop4 = TxOp(StartUSec=49000, StopUSec=74000, TxOpTimeout=txop_timeout, CenterFrequencyHz=center_frequency_hz, link_direction='down')
#     txop5 = TxOp(StartUSec=75000, StopUSec=86500, TxOpTimeout=txop_timeout, CenterFrequencyHz=center_frequency_hz, link_direction='up')
#     txop6 = TxOp(StartUSec=87500, StopUSec=99000, TxOpTimeout=txop_timeout, CenterFrequencyHz=center_frequency_hz, link_direction='down')
#
#     new_schedule = [txop1, txop2, txop3, txop4, txop5, txop6]