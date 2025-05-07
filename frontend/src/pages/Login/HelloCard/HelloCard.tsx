import { ReactNode } from "react"
import "./HelloCard.scss"

interface IHelloCardProps{
    children?: ReactNode
}

export const HelloCard = (props: IHelloCardProps) =>{
    return (
    <div>
        <div className="hello-body">
            <svg  viewBox="0 0 100% 100%" xmlns='http://www.w3.org/2000/svg' className="noise"> {/*svg карточка для текста*/}
                <filter id='noiseFilter'>
                    <feTurbulence 
                        type='fractalNoise' 
                        baseFrequency='0.85' 
                        numOctaves='6' 
                        stitchTiles='stitch' 
                    />
                </filter>
                <rect
                    width='100%'
                    height='100%'
                    preserveAspectRatio="xMidYMid meet"
                    filter='url(#noiseFilter)' 
                />
            </svg>
            <div>
                {props.children}
                
            </div>
        </div>
        <div className="hello-bg">
            <svg viewBox="0 0 100% 100%" xmlns='http://www.w3.org/2000/svg' className="noiseBg"> {/*svg карточка для фона*/}
                <filter id='noiseFilterBg'>
                    <feTurbulence 
                        type='fractalNoise'
                        baseFrequency='0.6'
                        stitchTiles='stitch' 
                />
                </filter>

                <rect
                    width='100%'
                    height='100%'
                    preserveAspectRatio="xMidYMid meet"
                    filter='url(#noiseFilterBg)' 
                />
            </svg>
            <svg xmlns="http://www.w3.org/2000/svg">
                <defs> {/*Для отрисовки плавающих объектов*/}
                    <filter id="goo">
                        <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" />
                        <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -8" result="goo" />
                        <feBlend in="SourceGraphic" in2="goo" />
                    </filter>
                </defs>
            </svg>
            <div className="gradients-container">
                <div className="g1"></div>
                <div className="g2"></div>
                <div className="g3"></div>
                <div className="g4"></div>
                <div className="g5"></div>
                <div className="interactive"></div>
            </div>
        </div>
    </div>
    )
}