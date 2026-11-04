model RoomThermal "Lesson 15 room as Modelica: C*der(T) = heater*Q_max - (T - T_out)/R (same as units.Room)"
  parameter Real T_out = 5 "outdoor temperature [degC]";
  parameter Real R = 0.008 "thermal resistance [K/W]";
  parameter Real C = 450000 "heat capacity [J/K]; tau = R*C = 3600 s";
  parameter Real Q_max = 3000 "heater power [W]";
  input Real heater "heater command 0..1 (set by the master)";
  output Real T(start = 15, fixed = true) "room temperature [degC]";
equation
  C*der(T) = heater*Q_max - (T - T_out)/R;
end RoomThermal;
