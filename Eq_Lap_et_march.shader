Shader "Unlit/NewUnlitShader"
{
    Properties
    {
         _Centre ("Centre",Vector) = (0,0,0)
         _Radius ("Radius", Range(0,10)) = 1
         _Hot ("Hot", Range(0,1)) = 1
         _Cold("Cold", Range(0,1)) = 0
         _X("X", Range(-10,10)) = 5
         _Accuracy ("Accuracy", Range(0,12)) = 10
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        LOD 100

        Pass
        {
            CGPROGRAM
            #include "Lighting.cginc"
            #pragma vertex vert
            #pragma fragment frag
            // make fog work
            #pragma multi_compile_fog

            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct v2f
            {
                float4 pos : SV_POSITION;//Clip space
                //UNITY_FOG_COORDS(1)
                float3 wPos : TEXCOORD1;//world position
            };

            float3 _Centre;
            fixed _Radius;
            float _Hot,_Cold,_X;
            int _Accuracy;
            

            float sphereDistance(float3 p)
            {
                return distance(p, _Centre) - _Radius;
            }
            fixed4 raymarch(float3 position, float3 direction)
            {
                float STEPS = 64;
                // Loop do raymarcher.
                for (int i = 0; i < STEPS; i++)
                {
                    float distance = sphereDistance(position);
                    if (distance < 0.001)
                        return i / (float)STEPS;
                        //to paint the ball in different depth
                    position += distance * direction;
                }
                return 0;
            }
            float F(float3 position){
                if(position.x > _X)return _Hot;
                return _Cold;
            }
            float SDFCurrent(float3 position){
               return distance(position, _Centre) - _Radius;
            }
            float random(float x)
            {
                float y = sin(x)*1000.0-floor(sin(x)*1000.0);
                return y;
            }
            float solve(float3 p0){
                //if (SDFCurrent(p0)>0) return 1;
                float epsilon = 0.01;
                float sum = 0;
                int walkSamples = (int)pow(2,_Accuracy);
                float pi = 3.1415926;
                for (int walk=0; walk<walkSamples; walk++){
                    float3 p = p0;
                    while(SDFCurrent(p) < -epsilon){
                        float internalRadius = - SDFCurrent(p);
                        float theta = 2 * pi * random(walk);
                        float phi = pi * random(walk+1.1);

                        p = float3(p.x + internalRadius * sin(theta) * cos(phi), p.y + internalRadius * sin(theta) * sin(phi), p.z + internalRadius * cos(theta));
                    }
                    sum += F(p)/walkSamples;
                }
                return sum;
            }
            
            v2f vert (appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                o.wPos = mul(unity_ObjectToWorld, v.vertex).xyz;
                return o;
            }

            fixed4 frag (v2f i) : SV_Target
            {
                float3 worldPosition = i.wPos;
                //float3 viewDirection = normalize(i.wPos - _WorldSpaceCameraPos);
                float now = solve(worldPosition);
                //return (1-raymarch(worldPosition, viewDirection)) * float4(1,1,1,1);
                //return solve(worldPosition) * float4(1,1,1,1);
                return now * (float4(1,1,1,1)-float4(0.2,0,0,1)) + float4(0.2,0,0,1);//decide the color of the material
            }
            ENDCG
        }
    }
}
