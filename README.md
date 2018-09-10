# Linus-Hershey-plotter
Using a Hershey font to print text with a line-us plotter

This is heavily based on the work of Stewart C. Russell, aka scruss, who posted the Hershey files and a Python decoding program [here](https://github.com/scruss/python-hershey) You can do what you like with the code, but according to Stewart  the following be should be kept in any distribution derived from the work of the Usenet Font Consortium:

```
USE RESTRICTION:
    This distribution of the Hershey Fonts may be used by anyone for
    any purpose, commercial or otherwise, providing that:
            1. The following acknowledgements must be distributed with
                    the font data:
                    - The Hershey Fonts were originally created by Dr.
                            A. V. Hershey while working at the U. S.
                            National Bureau of Standards.
                    - The format of the Font data in this distribution
                            was originally created by
                                    James Hurt
                                    Cognition, Inc.
                                    900 Technology Park Drive
                                    Billerica, MA 01821
                                    (mit-eddie!ci-dandelion!hurt)
            2. The font data in this distribution may be converted into
                    any other format *EXCEPT* the format distributed by
                    the U.S. NTIS (which organization holds the rights
                    to the distribution and use of the font data in that
                    particular format). Not that anybody would really
                    *want* to use their format... each point is described
                    in eight bytes as "xxx yyy:", where xxx and yyy are
                    the coordinate values as ASCII numbers.
```

## Using the program
To use the program just run it in Python 3.n. It uses the line-us.local device name so it should find your plotter on your local network. There are two font designs, a hand-drawn script design and a more convetional printed font. There are font designs for letters, digits and space. You can take a new line in your message by using the underscore character.  

Rob Miles 
