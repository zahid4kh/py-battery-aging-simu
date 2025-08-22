| Symbol | $c_{1}$ |       $c_{2}$       |       $c_{3}$        | $c_{4}$ |              $c_{5}$               |        $c_{6}$        | $m$  | $E_{a}$ |
|:------:|:-------:|:-------------------:|:--------------------:|:-------:|:----------------------------------:|:---------------------:|:----:|:-------:|
| Value  |  0.98   | $9.31 \cdot 10^{4}$ | $3.90 \cdot 10^{-3}$ |  0.20   |        $4.00 \cdot 10^{-3}$        | $34.50 \cdot 10^{-3}$ | 1.23 |  36.36  |
|  Unit  |         |         \%          |        $1/\%$        |   \%    | $h^{m} \, \%_{0}^{1-\tfrac{m}{2}}$ |           –           |  –   | kJ/mol  |

**Table 4.4:** List of cyclic aging model parameters.

---

The differential formulation of the model equation for the capacity loss due to cracking in the anode material $C_{\text{loss,AM}}$ is defined analogously to the Paris law:

$$
\frac{\partial C_{\text{loss,AM}}(\varnothing SoC, DoD)}
{\partial EFC}
= c_{5} \cdot \sigma(\varnothing SoC, DoD) \cdot
\sqrt{C_{\text{loss,AM}}}^{\,m}
$$

with the empirical model coefficients $c_{5}$ and $m$.

---

### Cyclic aging - current dependency

Compared to modeling the SEI growth or formation of lithium plating, there are significantly fewer validated studies modeling current rate dependent crack formation in the active material [33]. Purewal et al. [20] derived a proportionality between cell current and tensile stress at the particle surface based on Fick’s second law of diffusion. Analogously, the span of the stress intensity $\Delta K$ is extended by a linear current dependency. For the capacity loss change with the number of EFC it follows

$$
\frac{\partial C_{\text{loss,AM}}(\varnothing\,SoC,\,DoD,\,I)}
     {\partial EFC}
= c_{5}\,\big( I \cdot \sigma(\varnothing\,SoC,\,DoD) \cdot \sqrt{C_{\text{loss,AM}}} \big)^{m}
\tag{4.17}
$$


with the primitive function  

$$
C_{\text{loss,AM}}(\varnothing SoC, DoD, I) =
\frac{1}{I^{2} \cdot \sigma(\varnothing SoC, DoD)}
\cdot \left(
\frac{ -EFC \cdot (m - 2) \cdot c_{5} \cdot \sigma(\varnothing SoC, DoD)^{2} \cdot I^{2} }{2}
\right)^{\frac{-2}{m-2}}
\tag{4.18}
$$

For a physically meaningful result – a capacity loss that gradually increases with the number of cycles – the parameter $m$ must be in the range between two and zero.
