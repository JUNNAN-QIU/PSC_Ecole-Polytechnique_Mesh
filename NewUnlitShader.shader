Shader "Unlit/NewUnlitShader"
{
Properties
    {
        _Color("Color",Vector) = (1,1,1)
        _Centre ("Centre",Vector) = (0,0,0)
        _Radius ("Radius", Range(0,1)) = 0.8
        _SpecularPower("SpecularPower",Range(0,20)) = 4
        _Gloss("Gloss",Range(0,1)) = 0.8
    }
    SubShader
        {
            Blend SrcAlpha OneMinusSrcAlpha
            Tags { "RenderType" = "Transparent" "Queue" = "Transparent" }
            LOD 100

            Pass
            {
                CGPROGRAM
                #include "Lighting.cginc"

                #pragma vertex vert
                #pragma fragment frag

                #include "UnityCG.cginc"


                struct appdata
                {
                    float4 vertex : POSITION;
                    float2 uv : TEXCOORD0;
                };

                struct v2f {
                    float4 pos : SV_POSITION;    // Clip space
                    float3 wPos : TEXCOORD1;    // World position
                };

                float3 _Centre;
                fixed _Radius;
                fixed _SpecularPower;
                fixed _Gloss;
                fixed4 _Color;


                //估算距离
                float sphereDistance(float3 p)
                {
                    return distance(p, _Centre) - _Radius;
                }
                float3 normal(float3 p)
                {
                    const float eps = 0.01;
                    return normalize
                    (float3
                        (sphereDistance(p + float3(eps, 0, 0)) - sphereDistance(p - float3(eps, 0, 0)),
                            sphereDistance(p + float3(0, eps, 0)) - sphereDistance(p - float3(0, eps, 0)),
                            sphereDistance(p + float3(0, 0, eps)) - sphereDistance(p - float3(0, 0, eps))
                            )
                    );
                }

                fixed4 simpleLambertBlinn(fixed3 normal,float3 direction) {
                    fixed3 viewDirection = direction;
                    fixed3 lightDir = _WorldSpaceLightPos0.xyz;    // Light direction
                    fixed3 lightCol = _LightColor0.rgb;        // Light color
                    fixed NdotL = max(dot(normal, lightDir), 0);
                    fixed4 c;
                    // Specular
                    fixed3 h = (lightDir - viewDirection) / 2.;
                    fixed s = pow(dot(normal, h), _SpecularPower) * _Gloss;
                    c.rgb = _Color * lightCol * NdotL + s;
                    c.a = 1;                    
                    return c;
                }

                fixed4 renderSurface(float3 p, float3 direction)
                {
                    float3 n = normal(p);
                    return simpleLambertBlinn(n, direction);
                }


                //光线步进
                fixed4 raymarch(float3 position, float3 direction)
                {
                    float STEPS = 64;
                    float STEP_SIZE = 0.01;
                    // Loop do raymarcher.
                    for (int i = 0; i < STEPS; i++)
                    {
                        float distance = sphereDistance(position);
                        if (distance < 0.01)
                            //return i / (float)STEPS;
                            return renderSurface(position, direction);
                        position += distance * direction;
                    }
                    return 1;
                }
                // Vertex function
                v2f vert(appdata_full v)
                {
                    v2f o;
                    o.pos = UnityObjectToClipPos(v.vertex);
                    o.wPos = mul(unity_ObjectToWorld, v.vertex).xyz;
                    return o;
                }
                // Fragment function
                fixed4 frag(v2f i) : SV_Target
                {
                    float3 worldPosition = i.wPos;
                    float3 viewDirection = normalize(i.wPos - _WorldSpaceCameraPos);
                    return  raymarch(worldPosition, viewDirection);
                }
            ENDCG
            }
        }
}
