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
    def __init__(
        self, width, height,
        empty_house_rate, neighbour_similarity,
        n_iterations,
        races = None
    ):
        if races is None:
            races = 2

        self.width = width
        self.height = height
        self.races = races
        self.empty_house_rate = empty_house_rate
        self.neighbour_similarity = neighbour_similarity
        self.n_iterations = n_iterations
        self.empty_houses = []
        # agents are gonna live in the houses
        self.agents = {}
        self.data = {}
        self.changes = []

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
            return False
        else:
            return float(count_similar)/(count_similar+count_different) < self.neighbour_similarity

    def evove_one(self):

        self.current_iteration += 1
        self.prev_agents = copy.deepcopy(self.agents)
        n_changes = 0
        for agent in self.prev_agents:
            if self._is_unsatisfied(agent[0], agent[1]):
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