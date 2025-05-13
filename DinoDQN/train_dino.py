import sys
import torch
import numpy as np
from game import DinoEnv
from dino_agent import DQNAgent
import pygame
import os
import json

pygame.init()
font_path = os.path.join("assets", "Other", "PressStart2P-Regular.ttf")
font = pygame.font.Font(font_path, 16)
reward_log = []

# Ortam parametreleri
EPISODES = 4000
TARGET_UPDATE = 10

env = DinoEnv()
state_dim = 8
action_dim = 3
high_score = 0

agent = DQNAgent(state_dim, action_dim)

for episode in range(EPISODES):
    render = True
    state = env.reset()
    total_reward = 0
    step_count = 0
    done = False

    while not done:
        action = agent.act(state)
        next_state, reward, done = env.step(action)
        agent.memory.push(state, action, reward, next_state, done)
        score = step_count
        agent.train()
        state = next_state
        total_reward += reward
        step_count += 0.25

        if step_count > high_score:
            high_score = step_count

        if render:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            env.screen.fill((255, 255, 255))
            env.ground.draw(env.screen)
            env.dino.draw(env.screen)
            for obs in env.obstacles:
                obs.draw(env.screen)
                
            score_text = font.render(f"Score: {int(step_count):04}", True, (0, 0, 0))
            text_width = score_text.get_width()
            x_pos = 800 - text_width - 10
            env.screen.blit(score_text, (x_pos, 10))  

            episode_text = font.render(f"Episode: {(episode + 1):04}", True, (0, 0, 0))
            env.screen.blit(episode_text, (x_pos -30, 35)) 

            pygame.display.update()
            env.clock.tick(180)

    if agent.epsilon > agent.epsilon_min:
        agent.epsilon -= 0.01
        agent.epsilon = max(agent.epsilon_min, agent.epsilon)        

    print(f"Episode {episode + 1}: Reward = {total_reward}, Score = {step_count}, Epsilon = {agent.epsilon:.4f}")
    reward_log.append(total_reward)

    with open("reward_log.json", "w") as f:
        json.dump(reward_log, f)

    if episode % TARGET_UPDATE == 0:
        agent.update_target()

    # Modeli kaydet
    if (episode + 1) % 100 == 0:
        torch.save(agent.q_net.state_dict(), f"models/dino_dqn_ep{episode+1}.pth")
