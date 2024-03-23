#Torch
import torch
from tensordict.nn import TensorDictModule, TensorDictSequential
from tensordict.nn.distributions import NormalParamExtractor
from torch import nn

#Data
from torchrl.collectors import SyncDataCollector
from torchrl.data.replay_buffers import ReplayBuffer, TensorDictReplayBuffer, LazyTensorStorage, SamplerWithoutReplacement

#Modules
from torchrl.modules import ProbabilisticActor, ValueOperator, TanhNormal, MultiAgentMLP

#Objectives
from torchrl.objectives import ClipPPOLoss, ValueEstimators
from torchrl.objectives.value import GAE

#Multi-processing
from torch import multiprocessing
from torchrl.envs import RewardSum, TransformedEnv, check_env_specs, Transform

#Envs
from momentum_env.momentum_env import Momentum
from torchrl.envs import PettingZooWrapper

env = Momentum()
group_map = {"team0": ['player1', 'player2', 'player3'],
            "team1": ['player4', 'player5', 'player6']}

env = PettingZooWrapper(env, group_map=group_map)

is_fork = multiprocessing.get_start_method() == "fork"
device = (
    torch.device(0)
    if torch.cuda.is_available() and not is_fork
    else torch.device("cpu")
)

device = torch.device("cpu")

# Sampling
frames_per_batch = 6_000  # Number of team frames collected per training iteration
n_iters = 30  # Number of sampling and training iterations
total_frames = frames_per_batch * n_iters

# Training
num_epochs = 10  # Number of optimization steps per training iteration
minibatch_size = 100  # Size of the mini-batches in each optimization step
lr = 3e-4  # Learning rate
max_grad_norm = 1.0  # Maximum norm for the gradients

# PPO
clip_epsilon = 0.2  # clip value for PPO loss
gamma = 0.9  # discount factor
lmbda = 0.9  # lambda for generalised advantage estimation
entropy_eps = 1e-4

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

team0_policy = ProbabilisticActor(
    module = team0_policy_module,
    spec=env.action_spec["team0", "action"],
    in_keys = [("team0", "loc"), ("team0", "scale")],
    out_keys = [env.action_keys[0]],
    distribution_class = TanhNormal,
    distribution_kwargs = {
        "min": env.action_spec[env.action_keys[0]].space.low[0],
        "max": env.action_spec[env.action_keys[0]].space.high[0],
    },
    return_log_prob = True,
    log_prob_key = ("team0", "sample_log_prob"),
).to(device)

team0_critic_net = MultiAgentMLP(
    n_agent_inputs = env.observation_spec["team0", "observation"].shape[-1],
    n_agent_outputs=1,
    n_agents=3,
    centralised=True,
    share_params=True,
    device=device,
    depth=2,
    num_cells=128,
    activation_class=torch.nn.Tanh,
).to(device)

team0_critic = TensorDictModule(
    module=team0_critic_net,
    in_keys = [("team0", "observation")],
    out_keys = [("team0", "state_value")],
).to(device)

team0_loss_module = ClipPPOLoss(
    actor_network=team0_policy,
    critic_network=team0_critic,
    clip_epsilon=clip_epsilon,
    entropy_coef=entropy_eps,
    normalize_advantage=False,
)

team0_loss_module.set_keys(
    reward=env.reward_keys[0],
    action=env.action_keys[0],
    sample_log_prob=("team0", "sample_log_prob"),
    value=("team0", "state_value"),
    done=("team0", "done"),
    terminated = ("team0", "terminated"),
)

team0_loss_module.make_value_estimator(
    ValueEstimators.GAE, gamma=gamma, lmbda=lmbda,
)
team0_GAE = team0_loss_module.value_estimator

team0_optim = torch.optim.Adam(team0_loss_module.parameters(), lr)

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

team1_policy = ProbabilisticActor(
    module = team1_policy_module,
    spec=env.action_spec["team1", "action"],
    in_keys = [("team1", "loc"), ("team1", "scale")],
    out_keys = [env.action_keys[1]],
    distribution_class = TanhNormal,
    distribution_kwargs = {
        "min": env.action_spec[env.action_keys[1]].space.low[0],
        "max": env.action_spec[env.action_keys[1]].space.high[0],
    },
    return_log_prob = True,
    log_prob_key = ("team1", "sample_log_prob"),
).to(device)

team1_critic_net = MultiAgentMLP(
    n_agent_inputs = env.observation_spec["team1", "observation"].shape[-1],
    n_agent_outputs=1,
    n_agents=3,
    centralised=True,
    share_params=True,
    device=device,
    depth=2,
    num_cells=128,
    activation_class=torch.nn.Tanh,
).to(device)

team1_critic = TensorDictModule(
    module=team1_critic_net,
    in_keys = [("team1", "observation")],
    out_keys = [("team1", "state_value")],
).to(device)

team1_loss_module = ClipPPOLoss(
    actor_network=team1_policy,
    critic_network=team1_critic,
    clip_epsilon=clip_epsilon,
    entropy_coef=entropy_eps,
    normalize_advantage=False,
)

team1_loss_module.set_keys(
    reward=env.reward_keys[1],
    action=env.action_keys[1],
    sample_log_prob=("team1", "sample_log_prob"),
    value=("team1", "state_value"),
    done=("team1", "done"),
    terminated = ("team1", "terminated"),
)

team1_loss_module.make_value_estimator(
    ValueEstimators.GAE, gamma=gamma, lmbda=lmbda,
)
team1_GAE = team1_loss_module.value_estimator

team1_optim = torch.optim.Adam(team0_loss_module.parameters(), lr)

episode_reward_mean_list = []

policy = TensorDictSequential(
   team0_policy,
   team1_policy,
)

collector = SyncDataCollector(
    env,
    policy,
    device=device,
    storing_device=device,
    frames_per_batch = frames_per_batch,
    total_frames=total_frames,
)

replay_buffer = ReplayBuffer(
    storage=LazyTensorStorage(
        frames_per_batch,device=device,
    ),
    sampler=SamplerWithoutReplacement(),
    batch_size=minibatch_size,
)

episode_reward_mean_list = []

groups = ["team0", "team1"]

losses = {"team0": team0_loss_module, "team1": team1_loss_module}
gaes = {"team0": team0_GAE, "team1": team1_GAE}
optims = {"team0": team0_optim, "team1": team1_optim}

for tensordict_data in collector:
    tensordict_data.set(
        ("next", "team0", "done"),
        tensordict_data.get(("next", "done"))
        .unsqueeze(-1)
        .expand(tensordict_data.get_item_shape(("next", env.reward_keys[0]))),
    )
    tensordict_data.set(
        ("next", "team0", "terminated"),
        tensordict_data.get(("next", "terminated"))
        .unsqueeze(-1)
        .expand(tensordict_data.get_item_shape(("next", env.reward_keys[0]))),
    )

    tensordict_data.set(
        ("next", "team1", "done"),
        tensordict_data.get(("next", "done"))
        .unsqueeze(-1)
        .expand(tensordict_data.get_item_shape(("next", env.reward_keys[1]))),
    )
    tensordict_data.set(
        ("next", "team1", "terminated"),
        tensordict_data.get(("next", "terminated"))
        .unsqueeze(-1)
        .expand(tensordict_data.get_item_shape(("next", env.reward_keys[1]))),
    )
    
    # We need to expand the done and terminated to match the reward shape (this is expected by the value estimator)

    for group in groups:

        if group == "team0":
            excluded_group = "team1"
        else:
            excluded_group = "team0"

        loss_module = losses[group]
        gae = gaes[group]
        optim = optims[group]
    
        with torch.no_grad():
            gaes[group](
                tensordict_data,
                params=loss_module.critic_network_params,
                target_params=loss_module.target_critic_network_params,
            )  # Compute GAE and add it to the data
    
        data_view = tensordict_data.reshape(-1)  # Flatten the batch size to shuffle data
        replay_buffer.extend(data_view)

        for _ in range(num_epochs):
            for _ in range(frames_per_batch // minibatch_size):
                subdata = replay_buffer.sample()
                subdata.exclude((excluded_group))
                loss_vals = loss_module(subdata)
                
                loss_value = (
                    loss_vals["loss_objective"]
                    + loss_vals["loss_critic"]
                    + loss_vals["loss_entropy"]
                )
    
                loss_value.backward()
    
                torch.nn.utils.clip_grad_norm_(
                    loss_module.parameters(), max_grad_norm
                )  # Optional
    
                optim.step()
                optim.zero_grad()
                
    collector.update_policy_weights_()

torch.save(team0_policy, "team0_v2.pt")
torch.save(team1_policy, "team1_v2.pt")