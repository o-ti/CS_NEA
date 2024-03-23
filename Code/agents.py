import torch

from tensordict import TensorDict
from tensordict.nn import TensorDictModule, TensorDictSequential
from tensordict.nn.distributions import NormalParamExtractor
from torch import nn

from torchrl.modules import ProbabilisticActor, ValueOperator, TanhNormal, MultiAgentMLP
from torch import multiprocessing
from torchrl.envs import RewardSum, TransformedEnv, check_env_specs, Transform

from training.momentum_env.momentum_env import Momentum
from torchrl.envs import PettingZooWrapper

class MomentumAgents:

    def __init__(self, difficulty):
        env = Momentum()
        self.group_map = {"team0": ['player1', 'player2', 'player3'],
                    "team1": ['player4', 'player5', 'player6']}

        env = PettingZooWrapper(env, group_map=self.group_map)
        device = torch.device("cpu")


        team0_policy_net = torch.nn.Sequential(
            MultiAgentMLP(
                n_agent_inputs=env.observation_spec["team0", "observation"].shape[-1],
                n_agent_outputs = 2 * 4,
                n_agents = 3,
                centralised = False,
                share_params = False,
                device=device,
                depth=2,
                num_cells = 128,
                activation_class = torch.nn.Tanh,
            ),
            NormalParamExtractor(),
        ).to(device)

        team0_policy_module = TensorDictModule(
            team0_policy_net,
            in_keys = [("team0", "observation")],
            out_keys = [("team0", "loc"), ("team0", "scale")],
        ).to(device)

        self.team0_policy = ProbabilisticActor(
            module = team0_policy_module,
            spec=env.action_spec["team0", "action"],
            in_keys = [("team0", "loc"), ("team0", "scale")],
            out_keys = [env.action_keys[0]],
            distribution_class = TanhNormal,
            distribution_kwargs = {
                "min": env.action_spec[env.action_keys[0]].space.low[0],
                "max": env.action_spec[env.action_keys[0]].space.high[0],
            },
        ).to(device)

        team1_policy_net = torch.nn.Sequential(
            MultiAgentMLP(
                n_agent_inputs=env.observation_spec["team1", "observation"].shape[-1],
                n_agent_outputs = 2 * 4,
                n_agents = 3,
                centralised = False,
                share_params = False,
                device=device,
                depth=2,
                num_cells = 128,
                activation_class = torch.nn.Tanh,
            ),
            NormalParamExtractor(),
        ).to(device)

        team1_policy_module = TensorDictModule(
            team1_policy_net,
            in_keys = [("team1", "observation")],
            out_keys = [("team1", "loc"), ("team1", "scale")],
        ).to(device)

        self.team1_policy = ProbabilisticActor(
            module = team1_policy_module,
            spec=env.action_spec["team1", "action"],
            in_keys = [("team1", "loc"), ("team1", "scale")],
            out_keys = [env.action_keys[1]],
            distribution_class = TanhNormal,
            distribution_kwargs = {
                "min": env.action_spec[env.action_keys[1]].space.low[0],
                "max": env.action_spec[env.action_keys[1]].space.high[0],
            },
        ).to(device)


        self.groups = ["team0", "team1"]

        friendlyModelPaths = {
            0: "D:\\OjasWork\\OjasWork\\CS_NEA\\Momentum\\team0_v11.pt",
            1: "D:\\OjasWork\\OjasWork\\CS_NEA\\Momentum\\team0_v12.pt",
        }

        enemyModelPaths = {
            0: "D:\\OjasWork\\OjasWork\\CS_NEA\\Momentum\\team1_v11.pt",
            1: "D:\\OjasWork\\OjasWork\\CS_NEA\\Momentum\\team1_v12.pt",
        }

        friendlyDifficulty = difficulty[0]
        enemyDifficulty = difficulty[1]

        self.team0_policy = torch.load(friendlyModelPaths[friendlyDifficulty]).to(device)
        self.team1_policy = torch.load(enemyModelPaths[enemyDifficulty]).to(device)

        self.policy = TensorDictSequential(
           self.team0_policy,
           self.team1_policy,
        )

if __name__ == "__main__":
    m = MomentumAgents()

    #Create the environment
    env = Momentum()

    #Use the PettingZooWrapper for TorchRL
    env = PettingZooWrapper(env, group_map=m.group_map)

    #Set device
    device = torch.device("cpu")

    #Create instance of all agents
    m = MomentumAgents()

    #Reset the env
    td = env.reset()

    #
    min_td = TensorDict(
        {
        "team0": 
            {
                "observation": td["team0", "observation"]
            },
        "team1": 
            {
                "observation": td["team1","observation"]
            },
        }, 
        batch_size=torch.Size([]),
    )

    print(m.team0_policy(min_td)["team0", "action"])
    print(m.team1_policy(min_td)["team1", "action"])