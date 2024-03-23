from torchrl.envs import EnvBase
#from momentum_env.weapon import Weapon, Shotgun, AssaultRifle, SniperRifle
#from momentum_env.player import Player
#from momentum_env.block import Block
#from momentum_env.utils import Utility as U
import numpy as np

import functools
from copy import copy

from math import pi

from torchrl.data import BoundedTensorSpec, UnboundedContinuousTensorSpec


class DemoEnv(EnvBase):

    def __init__(self, batch_size=(), device=None, **kwargs):

        agent_i_action_spec = BoundedTensorSpec(
            
        )

        agent_i_observation_spec = BoundedContinuousTensorSpec()

        self.action_specs = []
        self.observation_specs = []

        for i in range(env.n_agents):
            action_specs.append(agent_i_action_spec)
            observation_specs.append(agent_i_observation_spec)
            reward_specs.append(agent_i_reward_spec)


        pass

