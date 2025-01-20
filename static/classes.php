<?php
class Island
{
    public $islandName;
    public $longDesc;
    public $content;
    public $contentImage;
    public $personalityImage;
    public $islandContentID;
    public $islandOfPersonalityID;
    public $color;
//CONSTRUCTOR FUNCTION
    public function __construct($islandName, $longDesc, $content, $contentImage, $personalityImage, $islandContentID, $islandOfPersonalityID, $color)
    {
        $this->islandName = $islandName;
        $this->longDesc = $longDesc;
        $this->content = $content;
        $this->contentImage = $contentImage;
        $this->personalityImage = $personalityImage;
        $this->islandContentID = $islandContentID;
        $this->islandOfPersonalityID = $islandOfPersonalityID;
        $this->color = $color;
    }
//FUNCTIONS
    public function generatePersonalityHeader()
    {
        return '
        <hr>
            <div class="parallax-personalities d-flex align-items-center justify-content-center" id = "'. $this->islandName .'" style = "background-image: url('. $this->personalityImage .');">
    <span class="text-white display-4 label">
      ' . $this->islandName . '
    </span>
  </div>
  <div class="container py-5" id="leisure">
    <p class="text-center fs-6">
      ' . $this->longDesc . '
    </p>
    <div class="row mt-5 d-flex justify-content-center">
        ';
    }
    public function generateContentCard()
{
    return '
       


        <div class="col-lg-4 col-md-4 col-sm-12 hover-effect" id="'.$this->color.'" onclick="showModal(this)">
                <img src="'. $this->contentImage .'" class="img-fluid hover-opacity"
                    alt="' . $this->content . '">

                <div class="overlay" style="background-color: black;">
                    <p class="text"></p>
                </div>
            </div>
    ';
}
    public static function  closePersonalitySection()
    {
        return '
        </div>
        </div>
        ';
    }
}
?>