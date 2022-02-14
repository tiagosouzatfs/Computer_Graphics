from pathlib import Path
from OpenGL import GL as gl
from OpenGL import GLU as glu
from OpenGL import GLUT as glut

from camera import Camera
import numpy as np
import cv2

from keyboard_controler import KeyboardController
from gl_models import arm_model, floor_model
from arm_angles import ArmAngles


"""
Por padrão inicia-se
a janela em 800x600, mas
é possível redimensiona-la
durante a aplicação
"""
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

"""
Para que o caminho até a imagem
seja independente do sistema operacional
usa-se a classe Path do python, mas
é bom lembrar que esse script deve ser
executado dentro do diretório projeto_final
"""
FLOOR_IMAGE_PATH = Path('images').joinpath('piso_2.jpeg')
METAL_IMAGE_PATH = Path('images').joinpath('metal.jpeg')


def reshape(width: int,  height: int):
    """Callback chamando no momento que a tela é redimensionada"""
    global WINDOW_WIDTH, WINDOW_HEIGHT

    WINDOW_WIDTH = width
    WINDOW_HEIGHT = height
    print(f'width: {width} height: {height}')

    """
        ViewPort é o local da área a ser renderizada pelo OpenGL
        no caso pegou-se a janela toda
    """
    gl.glViewport(0, 0, width, height)

    """
        Cria-se uma visão em perspectiva para dar uma idea de
        profundidade no mundo 3D
    """
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    glu.gluPerspective(70.0, width/height, 0.1, 30.0)
    gl.glMatrixMode(gl.GL_MODELVIEW)


def opengl_init():
    """
        É nessa função que foi colocada a configuração inicial do OpenGL.
    """

    """
        Configurando a cor que será usada para limpar a tela antes de desenhar os objetos 
    """
    gl.glClearColor(0.07, 0.13, 0.17, 1.0)
    """ habilita-se a profundidade,  ou seja x,y,z"""
    gl.glEnable(gl.GL_DEPTH_TEST)

    """Configurações para habilitar a textura"""
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    gl.glShadeModel(gl.GL_FLAT)
    gl.glEnable(gl.GL_TEXTURE_2D)


def window_init():
    """
        Configurações iniciais do gestor de janelas GLUT
        basicamente a janela se posiciona na
        posição:
            x: 400
            y: 400
        foi colocado o nome da janela, que ela possui profundidade e que renderiza em RGBA
    """
    glut.glutInit()
    glut.glutInitDisplayMode(
        glut.GLUT_RGBA | glut.GLUT_DEPTH | glut.GLUT_DOUBLE | glut.GLUT_ALPHA)
    glut.glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glut.glutCreateWindow("Braco Robotico")
    glut.glutPositionWindow(400, 400)


def load_texture(image_path: Path) -> int:
    """
        carrega uma textura através de uma imagem em qualquer formato suportado pelo OpenCV. 
    """

    # segundo o OpenCV a imagem está em BGR
    image: np.ndarray = cv2.imread(str(image_path))

    """cria-se um id de textura
      define-se a textura que deve ser selecionada pelo OpenGL 
      carrega-se a textura no formado de imagem
      configura-se os parâmetros da textura

       """
    texture = gl.glGenTextures(1)

    gl.glBindTexture(gl.GL_TEXTURE_2D, texture)

    gl.glTexImage2D(gl.GL_TEXTURE_2D,
                    0,
                    gl.GL_RGB,  # formato da saída
                    image.shape[0],
                    image.shape[1],
                    0,
                    gl.GL_BGR,  # formato da imagem
                    gl.GL_UNSIGNED_BYTE,
                    image)

    """
        Em glTexParameteri configura-se os parâmetros da textura;
        GL_REPEAT, implica que repete-se a mesma imagem infinitamente;
        GL_NEAREST, implica que a cor do pixel mais próxima é que vai ser escolhida
        é mais fácil de visualizar na referência:  https://learnopengl.com/Getting-started/Textures
    """
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)

    gl.glTexParameteri(
        gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(
        gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

    return texture


def main():

    window_init()

    opengl_init()

    camera = Camera()

    """instanciado os ângulos do braço, por padrão é tudo 0 graus"""
    arm_angles = ArmAngles()
    keyboard_controler = KeyboardController(arm_angles, camera)

    """
        Carregando as texturas, utilizou-se o OpenCV para
        carregá-las e, por conveniência, ambas as texturas têm os mesmos parâmetros.
    """

    floor_texture_id = load_texture(FLOOR_IMAGE_PATH)

    arm_texture_id = load_texture(METAL_IMAGE_PATH)

    def display():
        """
            Callback de visualização da janela glut
            Basicamente  limpa-se a tela, posiciona-se a camera e 
            é feito o desenho:
                o chão,
                o braço
                

            Informa-se ao gestor de janela GLUT, para trocar o buffer background para o front (glutSwapBuffers)
            chama-se a função display novamente. (glutPostRedisplay)
        """

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glPushMatrix()

        camera.look_at()  # a função gluLookAt com as posições e orientações da câmera

        floor_model.draw_floor(floor_texture_id)

        gl.glTranslatef(-3.0, 0.5, 0.0) #translada o braço
        arm_model.draw_arm(arm_angles, arm_texture_id)

        gl.glPopMatrix()

        glut.glutSwapBuffers()
        glut.glutPostRedisplay()

    """
       normal_keys_handler, special_keys_handler
       são funções callbacks que são chamadas no momento que uma tecla é pressionada.
    """
    def normal_keys_handler(key: bytes, x: int, y: int):
        keyboard_controler.key_press(key)

    def special_keys_handler(key: int, x: int, y: int):
        keyboard_controler.special_key_press(key)

    """ conjunto de funções do gerenciador de janelas"""
    glut.glutDisplayFunc(display)
    glut.glutReshapeFunc(reshape)
    
    glut.glutKeyboardFunc(normal_keys_handler)
    glut.glutSpecialFunc(special_keys_handler)

    glut.glutMainLoop()  # sequestra a aplicação até fechar a janela.


if __name__ == '__main__':
    main()
