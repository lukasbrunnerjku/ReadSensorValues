#version 330 core
out vec4 fragColor;

in vec2 texCoord;

// we could have multiple textures which we could mix
uniform sampler2D texture1;

uniform int hasTexture;

void main()
{
  if (hasTexture == 1)
    fragColor = texture(texture1, texCoord);
  else
    fragColor = vec4(0, 0, 0, 1);
}
