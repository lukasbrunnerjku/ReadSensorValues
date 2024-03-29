#version 330 core
out vec4 fragColor;

in vec2 texCoord;

// we could have multiple textures which we could mix
uniform sampler2D texture1;

void main()
{
  fragColor = texture(texture1, texCoord);
}
