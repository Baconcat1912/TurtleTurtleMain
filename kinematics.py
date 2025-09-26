from functools import total_ordering

#constants
g = 9.81
info_output = False


#turtle A's motion
class suvat():
    def __init__(self, ini_velo, acceleration, displacement, final_velo, time, height, direction):
        #gives the turtles suvat properties
        self.ini_velo = ini_velo
        self.acceleration = acceleration
        self.displacement = displacement
        self.final_velo = final_velo
        self.time = time
        self.height = height
        self.direction = direction
    #this function moves the turtles every frame
    def move(self):
        self.displacement = self.ini_velo * 0.001 + 0.5 * self.acceleration * 0.001 * 0.001
        self.final_velo = self.ini_velo + self.acceleration * 0.001
        self.ini_velo = self.final_velo
        #this make sure the displacement is tally correct while the turtle goes upwards
        if self.direction == "up":
            self.height = self.height + self.displacement
            if self.final_velo == 0:
                #vertex reached and flips the acceleration
                self.direction = 'down'
                self.acceleration = self.acceleration * -1
            else:
                self.direction = self.direction
        #this make sure the displacement is tally correct while the turtle goes downwards
        elif self.direction == "down":
            self.height = self.height - self.displacement
        else:
            return "Error"





Alpha = suvat(0, g, 0, 0, 0, 80, "down")
Beta = suvat(20, -1*g, 0 ,0, 0, 0, "up")

for tick in range(1,5000):
    if round(float(Alpha.height), 0) == 0 and Alpha.acceleration == g: #stops moving them when they hit the ground
        Alpha.height = 0
        Alpha.ini_velo = 0
        Alpha.acceleration = 0
        Alpha.final_velo = 0
    if round(float(Beta.height), 0) == 0 and Beta.acceleration == g:
        Beta.height = 0
        Beta.ini_velo = 0
        Alpha.acceleration = 0
        Beta.final_velo = 0
    #if their height is equal, output the results
    elif round(float(Alpha.height), 2) == round(float(Beta.height), 2) and info_output == False and False:#Resolve to false. Remove and False to print again
        print((tick/1000)-0.001)
        print("Alpha's initial velo: ", round(int(Alpha.ini_velo), 2), " final velo: ", round(int(Alpha.final_velo), 2),
              " displacement: ", round(int(Alpha.displacement), 2), " direction: ", Alpha.direction, " acceleration: ",
              round(int(Alpha.acceleration), 2), " height: ", Alpha.height)
        print("Beta's initial velo: ", round(int(Beta.ini_velo), 2), " final velo: ", round(int(Beta.final_velo), 2),
              " displacement: ", round(int(Beta.displacement), 2), " direction: ", Beta.direction, " acceleration: ",
              round(int(Beta.acceleration), 2), " height: ", Beta.height)
        info_output = True

    else:
        Alpha.move()
        Beta.move()