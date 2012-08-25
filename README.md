## *GILES*: the Great Internet Ludic Experience Server ##

Giles is a telnet gaming experience, meant to provide a platform for
playing various games both old and new with nothing more complicated
than a decent telnet client.

Chances are pretty good that:

    telnet ripley.thenexusproject.org 9435

will connect you to the current testing instance of Giles (unless
it's down).  Otherwise feel free to crank it up on your own.

Some screenshots:

<table>
   <tr>
      <td>
         <p align="center">
         <img src="http://blortblort.org/giles/set-screenshot.png" alt="Set screenshot" width="375px" height="250px">
         </p>
      </td>
      <td>
         <p align="center">
         <img src="http://blortblort.org/giles/y-screenshot.png" alt="Y screenshot" width="375px" height="250px">
         </p>
      </td>
   </tr>
   <tr>
      <td>
         <p align="center">
         A friendly game of Set.
         </p>
      </td>
      <td>
         <p align="center">
         Kibitzing a game of Y.
      </td>
   </tr>
</table>

Giles is written in Python and makes use of [Miniboa](http://code.google.com/p/miniboa/),
a Python telnet server implementation.

Miniboa is released under the Apache License, version 2.0.  Giles
itself is released under the AGPL, version 3.
