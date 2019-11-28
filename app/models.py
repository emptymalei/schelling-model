import itertools
import random
import copy
import logging

# import matplotlib.pyplot as plt

logging.basicConfig()
logger = logging.getLogger('models')
logger.setLevel(logging.WARNING)


class Schelling():
    """
    Scheling model of segragation

    Reference: https://www.binpress.com/simulating-segregation-with-python/

    :param width: width of the grid to put living spaces
    :param height: height of the grid to put living spaces
    :param empty_house_rate: percentage of houses that are empty
    :param :
    """
    def __init__(self, model = None):

        if model is None:
            model = {"races": 2}

        # {
        #     "width": self.width,
        #     "height": self.height,
        #     "empty_house_rate": self.empty_house_rate,
        #     "neighbour_similarity": self.neighbour_similarity,
        #     "n_iterations": self.n_iterations,
        #     "races": self.races,
        #     "empty_houses": self.empty_houses,
        #     "agents": self.agents,
        #     "data": self.data,
        #     "changes": self.changes
        # }

        if not model.get('agents'):
            agents = {}
        else:
            agents = self._reload_agents(model.get('agents'))
            print("Using agents: ", agents)

        if model.get("empty_house_rate") is None:
            empty_house_rate = 0.2
        else:
            empty_house_rate = model.get("empty_house_rate")

        if not model.get("empty_houses"):
            empty_houses = []
        else:
            empty_houses = model.get("empty_houses")
            empty_houses = [tuple(i) for i in empty_houses]

        self.width = model.get("width") or 20
        self.height = model.get("height") or 20
        self.races = model.get("races") or 2
        self.empty_house_rate = empty_house_rate
        self.neighbour_similarity = model.get("neighbour_similarity") or 0.6
        self.n_iterations = model.get("n_iterations") or 100
        self.empty_houses = empty_houses
        # agents are gonna live in the houses
        self.agents = agents
        self.data = model.get("data") or {}
        self.changes = model.get("changes") or []
        self.order_parameters = model.get("order_parameters") or []
        self.current_iteration = model.get('current_iteration') or 0

    @staticmethod
    def _distribute_houses(locations, empty_house_rate):
        """
        _distribute_houses will distribute houses on the list of locations

        We typically have occupied houses and empty houses. In principle,
        we could distribute the houses using a probability distributions.
        In this algorithm, we simply randomize the list then cut it into two halves.

        :param locations: list of locations such as [(0,0), (0,1)]
        :type locations: list
        """

        random.shuffle(locations)
        empty_houses_count = int(empty_house_rate * len(locations))

        empty_houses = locations[:empty_houses_count]
        occupied_houses = locations[empty_houses_count:]

        return empty_houses, occupied_houses

    @staticmethod
    def _distribute_races_to_house(houses, number_of_races, method = None):
        """
        _distribute_agents places the agents in the houses.

        divide the list of houses into sub lists for each races
        """

        if method is None:
            method = "chunk"

        if method == "chunk":
            k, m = divmod(len(houses), number_of_races)
            return (
                houses[i * k + min(i, m):(i + 1) * k + min(i + 1, m)]
                for i in range(number_of_races)
                )
        elif method == "interleave":
            return (
                houses[i::number_of_races]
                for i in range(number_of_races)
                )
        else:
            raise Exception("No method {} found".format(method))

    @staticmethod
    def _agents_dict_to_2d_array(agents_dict, width, height):
        """
        _agents_dict_to_2d_array converts the agents dictionary to 2d list

        :param agents_dict: agents dict with keys as tuple of coordinates
        :type agents_dict: dict
        :param width: width of the grid
        :type width: int
        :param height: height of the grid
        :type height: int
        :return: 2d list of the grid with each value being the agent race
        :rtype: list
        """
        res = [[0] * width] * height
        logger.debug(agents_dict)

        res = [
            [
                agents_dict.get((idx, idx_2), 0) for idx_2, val_2 in enumerate(val)
            ]
            for idx, val in enumerate(res)
        ]

        logger.debug("first line: {}".format(res[0]))
        logger.debug("last line: {}".format(res[-1]))

        return res

    @staticmethod
    def _serialize_agents(agents):

        return [{'key':k, 'value': v} for k, v in agents.items()]

    @staticmethod
    def _reload_agents(key_val):

        tuple_keys_dict = {tuple(i.get("key")): i.get("value") for i in key_val}

        return tuple_keys_dict

    def model_state(self):
        """save the current status of the model
        """
        # generate all possible combinations of the horizontal and vertical coordinates
        return {
            "width": self.width,
            "height": self.height,
            "races": self.races,
            "empty_house_rate": self.empty_house_rate,
            "neighbour_similarity": self.neighbour_similarity,
            "n_iterations": self.n_iterations,
            "empty_houses": self.empty_houses,
            "agents": self._serialize_agents(self.agents),
            "data": self.data,
            "changes": self.changes,
            "order_parameters": self.order_parameters,
            "current_iteration": self.current_iteration
        }

    def initialize(self):
        """allocate occupied and empty houses to to grid
        and populate agents of each race to the occupied houses
        """
        # generate all possible combinations of the horizontal and vertical coordinates
        self.all_houses = list(itertools.product(range(self.width),range(self.height)))

        # allocate houses on the grid:
        self.empty_houses, self.occupied_houses = self._distribute_houses(
            self.all_houses, self.empty_house_rate
            )
        houses_by_agent_race = list(self._distribute_races_to_house(
            self.occupied_houses, self.races
        ))

        for i in range(self.races):
            self.agents.update(
                {
                    ho:i+1 for ho in houses_by_agent_race[i]
                }
                )

        self.current_iteration = 0
        self.data = {
            0: self._agents_dict_to_2d_array(self.agents, self.width, self.height)
        }

    def _is_unsatisfied(self, x, y):
        """
        is_unsatisfied calculate the satisfactory index of each agent based on
         current neighbours.

        :param x: horizental coordinate, starts with 0
        :type x: int
        :param y: vertical coordinate, starts with 0
        :type y: int
        :return: boolean value of wether the agent is not satisfied
        :rtype: [type]
        """
        race = self.agents.get((x,y))
        count_similar = 0
        count_different = 0

        if x > 0 and y > 0 and (x-1, y-1) not in self.empty_houses:
            if self.agents[(x-1, y-1)] == race:
                count_similar += 1
            else:
                count_different += 1
        if y > 0 and (x,y-1) not in self.empty_houses:
            if self.agents[(x,y-1)] == race:
                count_similar += 1
            else:
                count_different += 1
        if x < (self.width-1) and y > 0 and (x+1,y-1) not in self.empty_houses:
            if self.agents[(x+1,y-1)] == race:
                count_similar += 1
            else:
                count_different += 1
        if x > 0 and (x-1,y) not in self.empty_houses:
            if self.agents[(x-1,y)] == race:
                count_similar += 1
            else:
                count_different += 1
        if x < (self.width-1) and (x+1,y) not in self.empty_houses:
            if self.agents[(x+1,y)] == race:
                count_similar += 1
            else:
                count_different += 1
        if x > 0 and y < (self.height-1) and (x-1,y+1) not in self.empty_houses:
            if self.agents[(x-1,y+1)] == race:
                count_similar += 1
            else:
                count_different += 1
        if x > 0 and y < (self.height-1) and (x,y+1) not in self.empty_houses:
            if self.agents[(x,y+1)] == race:
                count_similar += 1
            else:
                count_different += 1
        if x < (self.width-1) and y < (self.height-1) and (x+1,y+1) not in self.empty_houses:
            if self.agents[(x+1,y+1)] == race:
                count_similar += 1
            else:
                count_different += 1

        if (count_similar+count_different) == 0:
            return False, 0.0
        else:
            return float(count_similar)/(count_similar+count_different) < self.neighbour_similarity, float(count_similar)/(count_similar+count_different)

    def evove_one(self):

        self.current_iteration += 1
        self.prev_agents = copy.deepcopy(self.agents)
        n_changes = 0
        for agent in self.prev_agents:
            agent_is_satisfied, _ = self._is_unsatisfied(agent[0], agent[1])
            if agent_is_satisfied:
                agent_race = self.agents[agent]
                empty_house = random.choice(self.empty_houses)
                self.agents[empty_house] = agent_race
                del self.agents[agent]
                self.empty_houses.remove(empty_house)
                self.empty_houses.append(agent)
                n_changes += 1
        self.changes.append(n_changes)
        logger.debug("changes: {}".format(n_changes))
        self.data[self.current_iteration] = self._agents_dict_to_2d_array(
            self.agents, self.width, self.height
            )
        self.order_parameters.append(
            self._order_parameter()
        )

    def _order_parameter(self):
        """
        order_parameter calculates the
        """

        order_param = 0
        for agent in self.agents:
            agent_is_satisfied, agent_neighbour_similarity = self._is_unsatisfied(agent[0], agent[1])
            order_param += agent_neighbour_similarity

        return order_param/len(self.agents)

    def evolve(self):
        """
        evolve calculates the predefined number of steps
        """

        for i in range(self.n_iterations):
            self.evove_one()
            # check if we have reached equlibrium
            # not the best way but kind of works
            if self.changes[-1] == 0:
                break


if __name__ == "__main__":
    schelling_1 = Schelling(30, 30, 0.3, 0.8, 20, 2)
    schelling_1.initialize()

    print(schelling_1.data)

    schelling_1.evolve()
    print(schelling_1.data)

    # schelling_1.visualize()

    print("END OF GAME")