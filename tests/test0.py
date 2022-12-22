# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    test0.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: acampo-p <acampo-p@student.42urduliz.com>  +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2022/12/08 18:33:32 by acampo-p          #+#    #+#              #
#    Updated: 2022/12/22 19:44:40 by acampo-p         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import  math
import  matplotlib.pyplot as plt
import  numpy as np

x = np.random.lognormal(3, 1, 100)
fig = plt.hist(x, bins=10)
fig.savefig('test.png')
