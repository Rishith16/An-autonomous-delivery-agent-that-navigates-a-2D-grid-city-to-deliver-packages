# src/data/dynamic_obstacles.py
# existing DynamicObstacles kept, plus moving obstacle helpers

class DynamicObstacles:
    def __init__(self, schedules=None):
        self.schedules = schedules or []

    @classmethod
    def load_from_list(cls, schedules):
        return cls(schedules)

    def position_at(self, obs_id, t):
       for s in self.schedules:
            if s["id"] == obs_id:
              traj = s["trajectory"]
              start = s.get("start",0)
              idx = t - start
              if 0 <= idx < len(traj):
                return tuple(traj[idx])   
       return None


    def occupied_at(self, t):
        occ = set()
        for s in self.schedules:
            pos = self.position_at(s["id"], t)
            if pos:
                occ.add(tuple(pos))
        return occ


# ---------------- moving obstacle helper classes ----------------
class MovingObstacle:
    def __init__(self, trajectory, start=0, loop=True, obs_id=None):
        """
        trajectory: list of (r,c) positions, one per timestep
        start: timestep when this obstacle appears at trajectory[0]
        loop: if True, the trajectory repeats cyclically
        obs_id: optional identifier
        """
        self.trajectory = list(trajectory)
        self.start = start
        self.loop = loop
        self.id = obs_id

    def position_at(self, t):
        idx = t - self.start
        if idx < 0:
            return None
        if idx >= len(self.trajectory):
            if self.loop:
                idx = idx % len(self.trajectory)
            else:
                return None
        return self.trajectory[idx]


class MovingObstacleManager:
    def __init__(self, obstacles=None):
        # obstacles: list of MovingObstacle
        self.obstacles = obstacles or []

    @classmethod
    def load_from_list(cls, schedule_list):
        """
        schedule_list: list of dicts like:
        {"id": 1, "trajectory": [(r1,c1),(r2,c2),...], "start": 0, "loop": True}
        """
        obs = []
        for s in schedule_list:
            obs.append(MovingObstacle(
                trajectory=s.get("trajectory", []),
                start=s.get("start", 0),
                loop=s.get("loop", True),
                obs_id=s.get("id", None)
            ))
        return cls(obs)

    def occupied_at(self, t):
        occ = set()
        for o in self.obstacles:
            p = o.position_at(t)
            if p:
                occ.add(tuple(p))
        return occ

